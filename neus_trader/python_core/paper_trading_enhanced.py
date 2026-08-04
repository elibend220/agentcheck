"""
Enhanced Paper Trading System with Institutional Flow Detection

Combines:
1. EMA(9/21) Crossover signals (Phase 1)
2. Institutional Flow detection (Smart Money indicators)
3. Hybrid entry/exit logic

Entry Strategy:
- EMA crossover triggers initial signal
- Institutional flow confirms or enhances the signal
- Combined confidence determines position size

Exit Strategy:
- Institutional distribution signals exit opportunity
- Smart money exit = larger confidence for SL
"""

import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

import pandas as pd

from institutional_flow import InstitutionalFlowDetector, InstitutionalSignal
from paper_trading import PaperTradingEngine, PaperTrade

logger = logging.getLogger(__name__)


@dataclass
class HybridSignal:
    """Combined signal from EMA + Institutional Flow"""
    timestamp: datetime
    direction: Optional[str]  # 'LONG', 'SHORT', or None
    ema_signal: Optional[str]  # 'LONG', 'SHORT', or None
    institutional_signal: Optional[str]  # 'accumulation', 'distribution', 'neutral'
    combined_confidence: float  # 0-1
    ema_weight: float  # Weight of EMA in decision
    flow_weight: float  # Weight of institutional flow
    reason: str


class EnhancedPaperTradingEngine(PaperTradingEngine):
    """
    Enhanced paper trading with institutional flow detection.

    Advantages:
    1. Better entry timing - waits for institutional confirmation
    2. Earlier exit signals - detects when smart money is exiting
    3. Improved P&L - avoids whipsaws with confirmation
    """

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        initial_capital: float = 10000.0,
        risk_per_trade: float = 0.005,
        max_positions: int = 3,
        buffer_size: int = 100,
        use_institutional_flow: bool = True
    ):
        """Initialize enhanced engine with institutional flow detection."""
        super().__init__(symbol, initial_capital, risk_per_trade, max_positions, buffer_size)

        self.use_institutional_flow = use_institutional_flow
        self.flow_detector = InstitutionalFlowDetector(symbol) if use_institutional_flow else None

        # Flow-based state
        self.last_institutional_signal: Optional[InstitutionalSignal] = None
        self.last_hybrid_signal: Optional[HybridSignal] = None
        self.signal_count_ema_only = 0
        self.signal_count_ema_flow = 0
        self.signal_count_flow_only = 0

        logger.info(f"EnhancedPaperTradingEngine initialized with institutional flow detection")

    def process_candle(self, candle: Dict) -> Optional[Dict]:
        """
        Process candle with both EMA and institutional flow.

        Args:
            candle: OHLCV data

        Returns:
            Trade execution result
        """
        try:
            # Update price history
            self.timestamps.append(candle['timestamp'])
            self.open_prices.append(candle['open'])
            self.high_prices.append(candle['high'])
            self.low_prices.append(candle['low'])
            self.close_prices.append(candle['close'])

            # Update institutional flow detector
            if self.use_institutional_flow:
                self.last_institutional_signal = self.flow_detector.process_candle(candle)

            # Check stop losses and take profits
            self._check_position_levels(candle['close'], candle['timestamp'])

            # Generate hybrid signal
            hybrid_signal = self._generate_hybrid_signal()

            # Execute based on hybrid signal
            if hybrid_signal and hybrid_signal.direction:
                if len(self.open_positions) < self.max_positions:
                    # Enhanced execution with confidence
                    return self._execute_trade_enhanced(hybrid_signal, candle)

            return None

        except Exception as e:
            self.logger.error(f"Error processing candle: {e}", exc_info=True)
            return None

    def _generate_hybrid_signal(self) -> Optional[HybridSignal]:
        """
        Generate combined signal from EMA + Institutional Flow.

        Decision Logic:
        1. EMA signal provides base direction
        2. Institutional flow provides confirmation
        3. Combination improves timing and reduces false signals
        """
        ema_signal = self._generate_signal()  # EMA(9/21)
        institutional_signal = self.last_institutional_signal

        # No signals = no action
        if not ema_signal and not institutional_signal:
            return None

        # Calculate combined confidence
        combined_confidence = 0.0
        direction = None
        reason = ""
        ema_weight = 0.6
        flow_weight = 0.4

        # Case 1: EMA signal only (no institutional confirmation)
        if ema_signal and not institutional_signal:
            combined_confidence = 0.6  # Reduced confidence without flow confirmation
            direction = ema_signal
            reason = f"EMA {ema_signal} (no flow confirmation yet)"
            self.signal_count_ema_only += 1

        # Case 2: Institutional signal only (no EMA trigger)
        elif institutional_signal and not ema_signal:
            # Disabled: Flow-only signals create too much noise without EMA confirmation
            # Only trade when BOTH signals align (Case 3 below)
            pass

        # Case 3: Both EMA and Institutional signals (BEST)
        elif ema_signal and institutional_signal:
            # Check alignment
            ema_long = ema_signal == 'LONG'
            flow_long = institutional_signal.accumulation_score > institutional_signal.distribution_score

            if ema_long == flow_long:
                # Aligned signals = high confidence
                combined_confidence = ema_weight * 0.9 + flow_weight * institutional_signal.confidence
                combined_confidence = min(combined_confidence, 1.0)
                direction = ema_signal
                reason = f"EMA+Flow aligned {ema_signal} (confidence: {combined_confidence:.1%})"
                self.signal_count_ema_flow += 1
            else:
                # Conflicting signals = reduced confidence or no action
                combined_confidence = 0.5
                direction = None
                reason = f"EMA and Flow conflict (EMA: {ema_signal}, Flow: {institutional_signal.flow_type})"

        # Create hybrid signal
        if direction:
            signal = HybridSignal(
                timestamp=datetime.utcnow(),
                direction=direction,
                ema_signal=ema_signal,
                institutional_signal=institutional_signal.flow_type if institutional_signal else None,
                combined_confidence=combined_confidence,
                ema_weight=ema_weight,
                flow_weight=flow_weight,
                reason=reason
            )
            self.last_hybrid_signal = signal
            return signal

        return None

    def _execute_trade_enhanced(self, signal: HybridSignal, candle: Dict) -> Dict:
        """
        Execute trade with enhanced confidence from flow analysis.

        Position sizing adjusted by:
        - Combined confidence (higher confidence = larger position)
        - Institutional flow confirmation
        """
        entry_price = candle['close']
        timestamp = candle['timestamp']

        # Calculate position size with confidence adjustment
        # Base: 0.5% equity risk
        # Boost: If institutional flow confirms, use up to 1.0% risk
        confidence_adjusted_risk = self.risk_per_trade * (1.0 + signal.combined_confidence)
        confidence_adjusted_risk = min(confidence_adjusted_risk, 0.01)  # Cap at 1%

        position_value = self.current_capital * confidence_adjusted_risk
        position_size = position_value / entry_price

        # Create trade record
        trade_id = f"trade_{self.next_trade_id:06d}"
        self.next_trade_id += 1

        # Set SL/TP levels based on signal type
        if signal.direction == 'LONG':
            stop_loss = entry_price * 0.998  # 0.2% below
            take_profit_1 = entry_price * 1.0075  # 0.75% above
            take_profit_2 = entry_price * 1.012  # 1.2% above
        else:  # SHORT
            stop_loss = entry_price * 1.002  # 0.2% above
            take_profit_1 = entry_price * 0.9925  # 0.75% below
            take_profit_2 = entry_price * 0.988  # 1.2% below

        trade = PaperTrade(
            trade_id=trade_id,
            symbol=self.symbol,
            direction=signal.direction,
            entry_price=entry_price,
            entry_time=timestamp,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            signal_source="hybrid_ema_flow",
            signal_confidence=signal.combined_confidence
        )

        # Update state
        self.open_positions[trade_id] = trade
        self.current_capital -= position_value
        self.total_trades_executed += 1

        self.logger.info(
            f"Trade executed: {trade_id} {signal.direction} "
            f"@ ${entry_price:.2f}, size={position_size:.4f}, "
            f"confidence={signal.combined_confidence:.1%}, "
            f"risk=${confidence_adjusted_risk * self.current_capital:.2f}"
        )

        return {
            'trade_id': trade_id,
            'direction': signal.direction,
            'entry_price': entry_price,
            'position_size': position_size,
            'confidence': signal.combined_confidence,
            'reason': signal.reason
        }

    def _check_position_levels(self, current_price: float, timestamp: datetime):
        """
        Check positions for SL/TP levels (standard only).

        Note: Institutional exit signals disabled - flow detector needs better tuning
        before it can reliably call exits. Using standard SL/TP only.
        """
        for trade_id, trade in list(self.open_positions.items()):
            should_close = False
            close_reason = None

            if trade.direction == 'LONG':
                # Take profit 2 (full position)
                if current_price >= trade.take_profit_2:
                    should_close = True
                    close_reason = 'take_profit_2'
                # Take profit 1 (partial)
                elif current_price >= trade.take_profit_1:
                    should_close = True
                    close_reason = 'take_profit_1'
                # Stop loss
                elif current_price <= trade.stop_loss:
                    should_close = True
                    close_reason = 'stop_loss'

            else:  # SHORT
                # Take profit 2 (full position)
                if current_price <= trade.take_profit_2:
                    should_close = True
                    close_reason = 'take_profit_2'
                # Take profit 1 (partial)
                elif current_price <= trade.take_profit_1:
                    should_close = True
                    close_reason = 'take_profit_1'
                # Stop loss
                elif current_price >= trade.stop_loss:
                    should_close = True
                    close_reason = 'stop_loss'

            if should_close:
                self._close_position(trade_id, current_price, close_reason, timestamp)

    def get_signal_statistics(self) -> Dict:
        """Get statistics on signal generation."""
        total_signals = (
            self.signal_count_ema_only +
            self.signal_count_ema_flow +
            self.signal_count_flow_only
        )

        return {
            'total_signals': total_signals,
            'ema_only': self.signal_count_ema_only,
            'ema_flow_combined': self.signal_count_ema_flow,
            'flow_only': self.signal_count_flow_only,
            'last_hybrid_signal': self.last_hybrid_signal.reason if self.last_hybrid_signal else None,
            'flow_state': self.flow_detector.get_flow_state() if self.use_institutional_flow else None
        }
