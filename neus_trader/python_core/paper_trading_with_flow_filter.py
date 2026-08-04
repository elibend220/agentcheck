"""
Paper Trading with Institutional Flow Risk Filter

Combines:
1. Phase 2 EMA signals (proven to work)
2. Institutional flow detection (as FILTER, not signal generator)

Flow detection used ONLY for:
- Risk management: Reduce position size on distribution signals
- Bonus trades: Accumulation-only bonus positions
- Exit alerts: Informational warnings (not automatic closure)
"""

import logging
from typing import Optional, Dict
from datetime import datetime

from institutional_flow import InstitutionalFlowDetector
from paper_trading import PaperTradingEngine, PaperTrade

logger = logging.getLogger(__name__)


class PaperTradingWithFlowFilter(PaperTradingEngine):
    """
    Paper trading engine using EMA signals with institutional flow risk management.

    Key philosophy:
    - EMA drives entry/exit decisions (proven)
    - Institutional flow provides risk context only
    - Position sizing adjusted based on flow state
    - Exit alerts generated when flow distribution detected
    """

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        initial_capital: float = 10000.0,
        risk_per_trade: float = 0.01,  # Increased to 1% for meaningful sizing
        max_positions: int = 3,
        buffer_size: int = 100,
        use_flow_filter: bool = True
    ):
        """Initialize with flow detection as optional filter."""
        super().__init__(symbol, initial_capital, risk_per_trade, max_positions, buffer_size)

        self.use_flow_filter = use_flow_filter
        self.flow_detector = InstitutionalFlowDetector(symbol) if use_flow_filter else None
        self.last_flow_state = None

        logger.info(f"PaperTradingWithFlowFilter initialized")
        logger.info(f"  EMA signals: ON (primary driver)")
        logger.info(f"  Flow filter: {'ON (risk management only)' if use_flow_filter else 'OFF'}")

    def process_candle(self, candle: Dict) -> Optional[Dict]:
        """
        Process candle with EMA signals + flow-based risk management.

        Flow detection used for:
        1. Position sizing adjustment (reduce on distribution)
        2. Risk alerts (log when smart money exiting)
        3. Bonus opportunities (trade accumulation patterns)
        """
        try:
            # Update price history
            self.timestamps.append(candle['timestamp'])
            self.open_prices.append(candle['open'])
            self.high_prices.append(candle['high'])
            self.low_prices.append(candle['low'])
            self.close_prices.append(candle['close'])

            # Update flow detector (purely informational)
            if self.use_flow_filter:
                self.flow_detector.process_candle(candle)
                self.last_flow_state = self.flow_detector.get_flow_state()

            # Check position levels
            self._check_position_levels(candle['close'], candle['timestamp'])

            # Generate EMA signal (primary)
            ema_signal = self._generate_signal()

            # Execute if EMA signals
            if ema_signal and len(self.open_positions) < self.max_positions:
                return self._execute_trade_with_flow_context(ema_signal, candle)

            return None

        except Exception as e:
            self.logger.error(f"Error processing candle: {e}", exc_info=True)
            return None

    def _execute_trade_with_flow_context(self, direction: str, candle: Dict) -> Dict:
        """
        Execute EMA trade with flow-adjusted position sizing.

        Risk management:
        - Distribution detected: Reduce position size to 50%
        - Accumulation detected: Increase position size to 120%
        - Neutral: Use base 1% risk
        """
        entry_price = candle['close']
        timestamp = candle['timestamp']

        # Base position sizing (1% risk)
        base_risk = self.risk_per_trade
        position_value = self.current_capital * base_risk

        # Adjust based on flow state
        position_multiplier = 1.0
        flow_context = ""

        if self.use_flow_filter and self.last_flow_state:
            if self.last_flow_state['distribution_score'] > 0.7:
                # Distribution: Smart money exiting - REDUCE position size
                position_multiplier = 0.5
                flow_context = f" (flow: distribution detected, sizing reduced)"
                self.logger.warning(
                    f"⚠️  Distribution signal: Reducing position to 50% size"
                )
            elif self.last_flow_state['accumulation_score'] > 0.7:
                # Accumulation: Smart money buying - INCREASE position size
                position_multiplier = 1.2
                flow_context = f" (flow: accumulation detected, sizing boosted)"
                self.logger.info(
                    f"✓ Accumulation signal: Boosting position to 120% size"
                )

        position_value = position_value * position_multiplier
        position_size = position_value / entry_price

        # Create trade
        trade_id = f"trade_{self.next_trade_id:06d}"
        self.next_trade_id += 1

        # SL/TP levels
        if direction == 'LONG':
            stop_loss = entry_price * 0.998  # 0.2%
            take_profit_1 = entry_price * 1.0075  # 0.75%
            take_profit_2 = entry_price * 1.012  # 1.2%
        else:  # SHORT
            stop_loss = entry_price * 1.002
            take_profit_1 = entry_price * 0.9925
            take_profit_2 = entry_price * 0.988

        trade = PaperTrade(
            trade_id=trade_id,
            symbol=self.symbol,
            direction=direction,
            entry_price=entry_price,
            entry_time=timestamp,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            signal_source="ema_with_flow_filter",
            signal_confidence=0.7  # EMA confidence
        )

        self.open_positions[trade_id] = trade
        self.current_capital -= position_value
        self.total_trades_executed += 1

        self.logger.info(
            f"Trade: {trade_id} {direction} @ ${entry_price:.2f}, "
            f"size={position_size:.4f}, risk=${position_value:.2f}{flow_context}"
        )

        return {
            'trade_id': trade_id,
            'direction': direction,
            'entry_price': entry_price,
            'position_size': position_size,
            'flow_context': flow_context
        }

    def get_flow_state(self) -> Optional[Dict]:
        """Get current institutional flow state."""
        if not self.use_flow_filter:
            return None
        return self.flow_detector.get_flow_state()

    def get_status(self) -> Dict:
        """Get trading status with flow context."""
        status = super().get_status() if hasattr(super(), 'get_status') else {}

        # Add flow information
        if self.use_flow_filter:
            status['flow_state'] = self.get_flow_state()

        return status
