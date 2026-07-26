"""
Paper Trading System

Executes Phase 1 signals in real-time using live Binance data without risking actual capital.
Simulates trading for validation and monitoring before production deployment.
"""

import logging
import asyncio
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PaperTrade:
    """Record of a simulated paper trade."""
    trade_id: str
    symbol: str
    direction: str  # LONG or SHORT
    entry_price: float
    entry_time: datetime
    position_size: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    duration_sec: Optional[float] = None
    signal_source: str = "phase1_ema"
    signal_confidence: float = 0.6

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['entry_time'] = self.entry_time.isoformat()
        data['exit_time'] = self.exit_time.isoformat() if self.exit_time else None
        return data


class PaperTradingEngine:
    """
    Real-time paper trading execution with live Binance data.

    Features:
    - Simulated trading without real capital
    - Live ETHUSDT price feed from Binance WebSocket
    - Phase 1 signal generation (EMA crossover)
    - Position tracking and P&L calculation
    - Real-time dashboard updates
    """

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        initial_capital: float = 10000.0,
        risk_per_trade: float = 0.005,  # 0.5% of equity
        max_positions: int = 3,
        buffer_size: int = 100
    ):
        """
        Initialize paper trading engine.

        Args:
            symbol: Trading pair (e.g., 'ETHUSDT')
            initial_capital: Starting simulated capital
            risk_per_trade: Risk per trade as fraction of equity
            max_positions: Maximum concurrent positions
            buffer_size: Number of candles to keep in history
        """
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.buffer_size = buffer_size
        self.logger = logging.getLogger('PaperTrading')

        # Price history for signal generation
        self.close_prices: deque = deque(maxlen=buffer_size)
        self.high_prices: deque = deque(maxlen=buffer_size)
        self.low_prices: deque = deque(maxlen=buffer_size)
        self.open_prices: deque = deque(maxlen=buffer_size)
        self.timestamps: deque = deque(maxlen=buffer_size)

        # Trading state
        self.open_positions: Dict[str, PaperTrade] = {}
        self.closed_trades: List[PaperTrade] = []
        self.next_trade_id = 0

        # Signal state (for EMA crossover)
        self._prev_ema9: Optional[float] = None
        self._prev_ema21: Optional[float] = None
        self.last_signal: Optional[str] = None
        self.last_signal_time: Optional[datetime] = None

        # Metrics
        self.total_signals_generated = 0
        self.total_trades_executed = 0
        self.starting_time = datetime.utcnow()

        self.logger.info(
            f"PaperTradingEngine initialized: {symbol}, "
            f"Capital=${initial_capital}, Risk={risk_per_trade*100}%"
        )

    def process_candle(self, candle: Dict) -> Optional[Dict]:
        """
        Process a new candle and generate trading signal.

        Args:
            candle: Dict with 'timestamp', 'open', 'high', 'low', 'close', 'volume'

        Returns:
            Trade execution result or None
        """
        try:
            # Update price history
            self.timestamps.append(candle['timestamp'])
            self.open_prices.append(candle['open'])
            self.high_prices.append(candle['high'])
            self.low_prices.append(candle['low'])
            self.close_prices.append(candle['close'])

            # Check stop losses and take profits
            self._check_position_levels(candle['close'], candle['timestamp'])

            # Generate trading signal
            signal = self._generate_signal()

            # Execute signal if valid
            if signal and len(self.open_positions) < self.max_positions:
                return self._execute_trade(signal, candle)

            return None

        except Exception as e:
            self.logger.error(f"Error processing candle: {e}", exc_info=True)
            return None

    def _generate_signal(self) -> Optional[str]:
        """
        Generate trading signal using EMA(9/21) crossover.

        Returns:
            'LONG', 'SHORT', or None
        """
        if len(self.close_prices) < 30:
            return None

        # Calculate EMAs
        ema9 = self._calc_ema(list(self.close_prices), 9)
        ema21 = self._calc_ema(list(self.close_prices), 21)

        if self._prev_ema9 is None:
            self._prev_ema9 = ema9
            self._prev_ema21 = ema21
            return None

        # Detect crossovers
        signal = None
        if self._prev_ema9 <= self._prev_ema21 and ema9 > ema21:
            signal = 'LONG'
        elif self._prev_ema9 >= self._prev_ema21 and ema9 < ema21:
            signal = 'SHORT'

        self._prev_ema9 = ema9
        self._prev_ema21 = ema21

        if signal:
            self.total_signals_generated += 1
            self.last_signal = signal
            self.last_signal_time = datetime.utcnow()

        return signal

    def _calc_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA for a list of prices."""
        if len(prices) < period:
            return prices[-1] if prices else 0.0

        multiplier = 2.0 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        return ema

    def _execute_trade(self, signal: str, candle: Dict) -> Dict:
        """
        Execute a paper trade.

        Args:
            signal: 'LONG' or 'SHORT'
            candle: Current candle data

        Returns:
            Trade execution details
        """
        entry_price = candle['close']

        # Calculate position size (0.5% risk per trade)
        position_value = self.current_capital * self.risk_per_trade
        position_size = position_value / entry_price

        # Create paper trade
        trade_id = f"paper_{self.next_trade_id}"
        self.next_trade_id += 1

        trade = PaperTrade(
            trade_id=trade_id,
            symbol=self.symbol,
            direction=signal,
            entry_price=entry_price,
            entry_time=candle['timestamp'],
            position_size=position_size,
            stop_loss=entry_price * (0.998 if signal == 'LONG' else 1.002),
            take_profit_1=entry_price * (1.0075 if signal == 'LONG' else 0.9925),
            take_profit_2=entry_price * (1.012 if signal == 'LONG' else 0.988),
            signal_source='phase1_ema',
            signal_confidence=0.6
        )

        self.open_positions[trade_id] = trade
        self.total_trades_executed += 1

        self.logger.info(
            f"Trade executed: {trade_id} {signal} {self.symbol} @ "
            f"${entry_price:.2f} × {position_size:.4f}"
        )

        return {
            'trade_id': trade_id,
            'direction': signal,
            'entry_price': entry_price,
            'position_size': position_size,
            'timestamp': candle['timestamp'].isoformat()
        }

    def _check_position_levels(self, current_price: float, timestamp: datetime):
        """Check and close positions at stop loss/take profit levels."""
        trades_to_close = []

        for trade_id, trade in list(self.open_positions.items()):
            should_close = False
            close_reason = None

            if trade.direction == 'LONG':
                if current_price <= trade.stop_loss:
                    should_close = True
                    close_reason = 'stop_loss'
                elif current_price >= trade.take_profit_1:
                    should_close = True
                    close_reason = 'take_profit'
            else:  # SHORT
                if current_price >= trade.stop_loss:
                    should_close = True
                    close_reason = 'stop_loss'
                elif current_price <= trade.take_profit_1:
                    should_close = True
                    close_reason = 'take_profit'

            if should_close:
                trades_to_close.append((trade_id, current_price, close_reason, timestamp))

        for trade_id, exit_price, reason, exit_time in trades_to_close:
            self._close_position(trade_id, exit_price, reason, exit_time)

    def _close_position(
        self,
        trade_id: str,
        exit_price: float,
        reason: str,
        exit_time: datetime
    ):
        """Close a position and record P&L."""
        if trade_id not in self.open_positions:
            return

        trade = self.open_positions.pop(trade_id)

        # Calculate P&L
        if trade.direction == 'LONG':
            pnl = (exit_price - trade.entry_price) * trade.position_size
        else:
            pnl = (trade.entry_price - exit_price) * trade.position_size

        # Update trade record
        trade.exit_price = exit_price
        trade.exit_time = exit_time
        trade.exit_reason = reason
        trade.pnl = pnl
        trade.pnl_pct = pnl / (trade.entry_price * trade.position_size)
        trade.duration_sec = (exit_time - trade.entry_time).total_seconds()

        # Update capital
        self.current_capital += pnl

        # Record closed trade
        self.closed_trades.append(trade)

        self.logger.info(
            f"Position closed: {trade_id} {reason} @ ${exit_price:.2f} "
            f"P&L: ${pnl:.2f} ({trade.pnl_pct*100:.2f}%)"
        )

    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'total_pnl_pct': 0.0,
                'current_capital': self.current_capital,
                'open_positions': len(self.open_positions),
                'duration_sec': (datetime.utcnow() - self.starting_time).total_seconds(),
                'total_signals': self.total_signals_generated,
                'total_trades_executed': self.total_trades_executed
            }

        winning = sum(1 for t in self.closed_trades if t.pnl > 0)
        losing = len(self.closed_trades) - winning
        total_pnl = sum(t.pnl for t in self.closed_trades)

        return {
            'total_trades': len(self.closed_trades),
            'winning_trades': winning,
            'losing_trades': losing,
            'win_rate': winning / len(self.closed_trades) if self.closed_trades else 0.0,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl / self.initial_capital,
            'current_capital': self.current_capital,
            'open_positions': len(self.open_positions),
            'duration_sec': (datetime.utcnow() - self.starting_time).total_seconds(),
            'total_signals': self.total_signals_generated,
            'total_trades_executed': self.total_trades_executed,
            'best_trade': max(self.closed_trades, key=lambda t: t.pnl).pnl if self.closed_trades else 0.0,
            'worst_trade': min(self.closed_trades, key=lambda t: t.pnl).pnl if self.closed_trades else 0.0,
            'avg_trade_pnl': total_pnl / len(self.closed_trades) if self.closed_trades else 0.0,
            'last_signal': self.last_signal,
            'last_signal_time': self.last_signal_time.isoformat() if self.last_signal_time else None
        }

    def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        return [
            {
                'trade_id': t.trade_id,
                'direction': t.direction,
                'entry_price': t.entry_price,
                'entry_time': t.entry_time.isoformat(),
                'position_size': t.position_size,
                'stop_loss': t.stop_loss,
                'take_profit_1': t.take_profit_1,
                'take_profit_2': t.take_profit_2,
                'signal_source': t.signal_source
            }
            for t in self.open_positions.values()
        ]

    def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """Get closed trades history."""
        recent_trades = self.closed_trades[-limit:] if limit else self.closed_trades
        return [t.to_dict() for t in recent_trades]

    def export_session(self, output_path: str):
        """Export paper trading session to JSON."""
        session_data = {
            'symbol': self.symbol,
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'session_start': self.starting_time.isoformat(),
            'session_end': datetime.utcnow().isoformat(),
            'duration_hours': (datetime.utcnow() - self.starting_time).total_seconds() / 3600,
            'metrics': self.get_metrics(),
            'open_positions': self.get_positions(),
            'closed_trades': self.get_trade_history(),
            'total_trades': len(self.closed_trades) + len(self.open_positions)
        }

        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)

        self.logger.info(f"Session exported to {output_path}")
