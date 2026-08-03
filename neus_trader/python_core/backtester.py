"""
Historical Backtesting Framework

Replay historical market data through trading engine to validate performance.
Supports both Phase 1 (single agent) and Phase 2 (multi-agent) modes.
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import csv
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BacktestMetrics:
    """Performance metrics from backtest."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_pct: float
    max_drawdown_pct: float
    sharpe_ratio: Optional[float]
    avg_trade_duration_sec: int
    best_trade_pnl: float
    worst_trade_pnl: float
    consecutive_losses: int
    equity_peak: float
    final_equity: float
    trades: List[Dict]


class HistoricalBacktester:
    """
    Replays historical candle data through trading engine.

    Supports:
    - Loading data from CSV or Binance API
    - Single-agent backtest (Phase 1)
    - Multi-agent backtest (Phase 2)
    - Detailed trade logging
    - Performance comparison
    """

    def __init__(self, engine, use_julia_agents: bool = False):
        """
        Initialize backtester.

        Args:
            engine: TradingScalpingEngine instance
            use_julia_agents: Whether to use Phase 2 multi-agent system
        """
        self.engine = engine
        self.use_julia_agents = use_julia_agents
        self.logger = logging.getLogger("Backtester")

        # State tracking
        self.trades: List[Dict] = []
        self.equity_history: List[float] = []
        self.candle_count = 0
        self.start_equity = engine.risk_manager.current_capital
        self._close_prices: List[float] = []
        self._prev_ema9: Optional[float] = None
        self._prev_ema21: Optional[float] = None

    def load_data_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load historical OHLCV data from CSV.

        Expected columns: timestamp, open, high, low, close, volume
        """
        try:
            df = pd.read_csv(csv_path)

            # Ensure required columns exist
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"CSV missing required columns: {required_cols}")

            # Parse timestamp
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                df['timestamp'] = pd.date_range(
                    start='2024-01-01',
                    periods=len(df),
                    freq='5min'
                )

            self.logger.info(f"Loaded {len(df)} candles from {csv_path}")
            return df

        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            raise

    def load_data_from_binance(
        self,
        symbol: str = 'ETHUSDT',
        interval: str = '5m',
        months: int = 12
    ) -> pd.DataFrame:
        """
        Load historical data from Binance API.

        Args:
            symbol: Trading pair (e.g., 'ETHUSDT')
            interval: Candle interval (e.g., '5m', '1h')
            months: How many months of history to load
        """
        try:
            from binance.client import Client

            client = Client()

            # Calculate date range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30 * months)

            self.logger.info(
                f"Fetching {symbol} {interval} data from {start_time} to {end_time}"
            )

            # Fetch klines (candles)
            klines = client.get_historical_klines(
                symbol,
                interval,
                start_str=start_time.isoformat(),
                end_str=end_time.isoformat()
            )

            # Parse into DataFrame
            data = []
            for kline in klines:
                data.append({
                    'timestamp': pd.Timestamp(kline[0], unit='ms'),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[7])
                })

            df = pd.DataFrame(data)
            self.logger.info(f"Loaded {len(df)} candles from Binance")
            return df

        except ImportError:
            self.logger.error("python-binance not installed: pip install python-binance")
            raise
        except Exception as e:
            self.logger.error(f"Failed to fetch Binance data: {e}")
            raise

    def run_backtest(self, candles: pd.DataFrame) -> BacktestMetrics:
        """
        Run backtest on historical candle data.

        Args:
            candles: DataFrame with OHLCV data

        Returns:
            BacktestMetrics with performance summary
        """
        self.logger.info(f"Starting backtest: {len(candles)} candles")
        self.logger.info(f"Mode: {'Phase 2 (Multi-Agent)' if self.use_julia_agents else 'Phase 1 (Single Agent)'}")

        self.trades = []
        self.equity_history = []
        self.candle_count = 0

        try:
            for idx, row in candles.iterrows():
                self._process_candle(row)

                # Log progress every 1000 candles
                if (idx + 1) % 1000 == 0:
                    equity = self.engine.risk_manager.current_capital
                    self.logger.info(
                        f"Processed {idx + 1}/{len(candles)} candles | Equity: ${equity:.2f}"
                    )

            # Close any open positions at end
            self._close_remaining_positions(candles.iloc[-1])

            # Calculate metrics
            metrics = self._calculate_metrics()

            self.logger.info(f"Backtest complete: {metrics.total_trades} trades, {metrics.win_rate*100:.1f}% win rate")
            return metrics

        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            raise

    def _process_candle(self, candle: pd.Series):
        """Process a single candle through the engine."""
        try:
            # Update engine state
            if not hasattr(self.engine, 'last_candle'):
                self.engine.last_candle = {}

            self.engine.last_candle = {
                'timestamp': candle['timestamp'],
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            }

            # Update volatility estimate
            if self.candle_count > 20:
                recent_closes = [candle['close']]  # Simplified
                returns = np.diff(recent_closes) if len(recent_closes) > 1 else []
                if len(returns) > 0:
                    if not hasattr(self.engine, 'volatility_estimate'):
                        self.engine.volatility_estimate = 0.0
                    self.engine.volatility_estimate = np.std(returns) * np.sqrt(252)

            # Check stop losses and take profits
            self._update_position_levels()

            # Generate trading signal (Phase 1 or Phase 2)
            if self.use_julia_agents and self.engine.julia_bridge:
                signal = self._get_signal_from_julia(candle)
            else:
                signal = self._get_signal_phase1(candle)

            # Execute signal
            if signal:
                self._execute_signal(signal, candle)

            # Track equity
            self.equity_history.append(self.engine.risk_manager.current_capital)
            self.candle_count += 1

        except Exception as e:
            self.logger.warning(f"Error processing candle: {e}")

    def _get_signal_phase1(self, candle: pd.Series) -> Optional[Dict]:
        """Generate signal using Phase 1 single agent logic."""
        self._close_prices.append(candle['close'])
        if len(self._close_prices) > 100:
            self._close_prices.pop(0)

        if len(self._close_prices) < 30:
            return None

        # Calculate EMAs
        ema9 = self._calc_ema(self._close_prices[-30:], 9)
        ema21 = self._calc_ema(self._close_prices[-30:], 21)

        if self._prev_ema9 is None:
            self._prev_ema9 = ema9
            self._prev_ema21 = ema21
            return None

        # Crossover signals
        if self._prev_ema9 <= self._prev_ema21 and ema9 > ema21:
            self._prev_ema9 = ema9
            self._prev_ema21 = ema21
            return {'direction': 'LONG', 'confidence': 0.6, 'source': 'ema_crossover'}
        elif self._prev_ema9 >= self._prev_ema21 and ema9 < ema21:
            self._prev_ema9 = ema9
            self._prev_ema21 = ema21
            return {'direction': 'SHORT', 'confidence': 0.6, 'source': 'ema_crossover'}

        self._prev_ema9 = ema9
        self._prev_ema21 = ema21
        return None

    def _calc_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA for a list of prices."""
        if len(prices) < period:
            return prices[-1] if prices else 0.0

        multiplier = 2.0 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        return ema

    def _get_signal_from_julia(self, candle: pd.Series) -> Optional[Dict]:
        """Generate signal using Phase 2 multi-agent consensus."""
        # Prepare data for Julia
        candles_data = [{
            'timestamp': candle['timestamp'].isoformat(),
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'volume': candle['volume']
        }]

        engine_state_data = {
            'symbol': getattr(self.engine, 'symbol', 'ETHUSDT'),
            'current_price': candle['close'],
            'capital': self.engine.risk_manager.current_capital,
            'equity': self.engine.risk_manager.current_capital,
            'drawdown_pct': 0.0,
            'open_positions': len(self.engine.open_positions),
            'total_trades': len(self.trades),
            'win_rate': self._get_current_win_rate(),
            'last_trade_pnl': 0.0,
            'is_running': True
        }

        decision = self.engine.julia_bridge.send_decision_request(
            candles_data, engine_state_data, {}
        )

        if decision and decision.direction != 'HOLD' and decision.risk_approved:
            return {
                'direction': decision.direction,
                'confidence': decision.confidence,
                'source': 'julia_consensus'
            }

        return None

    def _update_position_levels(self):
        """Check and update stop losses and take profits."""
        positions_to_close = []

        for trade_id, position in list(self.engine.open_positions.items()):
            current_price = self.engine.last_candle['close']

            # Check stop loss
            if position['direction'] == 'LONG':
                if current_price <= position['stop_loss']:
                    positions_to_close.append((trade_id, current_price, 'stop_loss'))
                elif current_price >= position['take_profit_1']:
                    positions_to_close.append((trade_id, current_price, 'take_profit'))

            else:  # SHORT
                if current_price >= position['stop_loss']:
                    positions_to_close.append((trade_id, current_price, 'stop_loss'))
                elif current_price <= position['take_profit_1']:
                    positions_to_close.append((trade_id, current_price, 'take_profit'))

        # Close positions
        for trade_id, exit_price, reason in positions_to_close:
            self._close_position(trade_id, exit_price, reason)

    def _execute_signal(self, signal: Dict, candle: pd.Series):
        """Execute a trading signal."""
        if len(self.engine.open_positions) >= 3:
            return  # Max 3 concurrent positions

        direction = signal['direction']
        confidence = signal.get('confidence', 0.5)
        entry_price = candle['close']

        # Conservative position sizing: 0.5% of equity per trade
        current_equity = self.engine.risk_manager.current_capital
        position_value = current_equity * 0.005  # 0.5% risk per trade
        position_size = position_value / entry_price  # Convert to units

        # Create trade
        trade_id = f"trade_{len(self.trades)}"
        trade = {
            'id': trade_id,
            'direction': direction,
            'entry_price': entry_price,
            'entry_time': candle['timestamp'],
            'position_size': position_size,
            'stop_loss': entry_price * (0.998 if direction == 'LONG' else 1.002),
            'take_profit_1': entry_price * (1.0075 if direction == 'LONG' else 0.9925),
            'take_profit_2': entry_price * (1.012 if direction == 'LONG' else 0.988),
            'confidence': confidence,
            'source': signal.get('source', 'unknown')
        }

        self.engine.open_positions[trade_id] = trade

    def _close_position(self, trade_id: str, exit_price: float, reason: str):
        """Close a position and record trade."""
        if trade_id not in self.engine.open_positions:
            return

        position = self.engine.open_positions[trade_id]

        # Calculate P&L
        if position['direction'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['position_size']
        else:
            pnl = (position['entry_price'] - exit_price) * position['position_size']

        # Record trade
        trade_record = {
            'id': trade_id,
            'direction': position['direction'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'pnl': pnl,
            'pnl_pct': pnl / position['entry_price'],
            'duration_sec': (self.engine.last_candle['timestamp'] - position['entry_time']).total_seconds(),
            'exit_reason': reason,
            'confidence': position['confidence'],
            'source': position['source']
        }

        self.trades.append(trade_record)

        # Update capital
        self.engine.risk_manager.current_capital += pnl

        # Remove from open positions
        del self.engine.open_positions[trade_id]

    def _close_remaining_positions(self, final_candle: pd.Series):
        """Close any remaining open positions at end of backtest."""
        for trade_id in list(self.engine.open_positions.keys()):
            self._close_position(trade_id, final_candle['close'], 'backtest_end')

    def _calculate_metrics(self) -> BacktestMetrics:
        """Calculate performance metrics from trades."""
        # Calculate drawdown from equity history (works even with no trades)
        max_drawdown_pct = 0.0
        equity_peak = self.start_equity
        if self.equity_history:
            equity_peak = self.start_equity
            running_max = self.start_equity
            for equity in self.equity_history:
                running_max = max(running_max, equity)
                drawdown = (equity - running_max) / running_max
                if drawdown < max_drawdown_pct:
                    max_drawdown_pct = drawdown
            equity_peak = running_max

        if not self.trades:
            return BacktestMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                total_pnl_pct=0.0,
                max_drawdown_pct=max_drawdown_pct,
                sharpe_ratio=None,
                avg_trade_duration_sec=0,
                best_trade_pnl=0.0,
                worst_trade_pnl=0.0,
                consecutive_losses=0,
                equity_peak=equity_peak,
                final_equity=self.start_equity if not self.equity_history else self.equity_history[-1],
                trades=[]
            )

        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        # P&L metrics
        total_pnl = sum(t['pnl'] for t in self.trades)
        final_equity = self.start_equity + total_pnl
        total_pnl_pct = total_pnl / self.start_equity

        # Trade durations
        durations = [t['duration_sec'] for t in self.trades]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Best/worst trades
        pnls = [t['pnl'] for t in self.trades]
        best_pnl = max(pnls) if pnls else 0.0
        worst_pnl = min(pnls) if pnls else 0.0

        # Consecutive losses
        consecutive_losses = 0
        for trade in reversed(self.trades):
            if trade['pnl'] < 0:
                consecutive_losses += 1
            else:
                break

        # Sharpe ratio (simplified)
        returns = np.diff(self.equity_history) if len(self.equity_history) > 1 else []
        sharpe_ratio = None
        if len(returns) > 1:
            daily_returns = np.array(returns) / np.array(self.equity_history[:-1])
            if np.std(daily_returns) > 0:
                sharpe_ratio = (np.mean(daily_returns) * 252) / (np.std(daily_returns) * np.sqrt(252))

        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_pnl_pct=total_pnl_pct,
            max_drawdown_pct=max_drawdown_pct,
            sharpe_ratio=sharpe_ratio,
            avg_trade_duration_sec=int(avg_duration),
            best_trade_pnl=best_pnl,
            worst_trade_pnl=worst_pnl,
            consecutive_losses=consecutive_losses,
            equity_peak=equity_peak,
            final_equity=final_equity,
            trades=self.trades
        )

    def _get_current_win_rate(self) -> float:
        """Get win rate from trades so far."""
        if not self.trades:
            return 0.5
        wins = sum(1 for t in self.trades if t['pnl'] > 0)
        return wins / len(self.trades)

    def export_results(self, output_path: str, metrics: BacktestMetrics):
        """Export backtest results to JSON and CSV."""
        # JSON summary
        summary = {
            'mode': 'Phase 2 (Multi-Agent)' if self.use_julia_agents else 'Phase 1 (Single Agent)',
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': metrics.win_rate,
            'total_pnl': metrics.total_pnl,
            'total_pnl_pct': metrics.total_pnl_pct,
            'max_drawdown_pct': metrics.max_drawdown_pct,
            'sharpe_ratio': metrics.sharpe_ratio,
            'avg_trade_duration_sec': metrics.avg_trade_duration_sec,
            'best_trade_pnl': metrics.best_trade_pnl,
            'worst_trade_pnl': metrics.worst_trade_pnl,
            'consecutive_losses': metrics.consecutive_losses,
            'equity_peak': metrics.equity_peak,
            'final_equity': metrics.final_equity
        }

        # Write JSON
        json_path = f"{output_path}_summary.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)

        # Write trades CSV
        csv_path = f"{output_path}_trades.csv"
        if metrics.trades:
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=metrics.trades[0].keys())
                writer.writeheader()
                writer.writerows(metrics.trades)

        self.logger.info(f"Results exported: {json_path}, {csv_path}")
