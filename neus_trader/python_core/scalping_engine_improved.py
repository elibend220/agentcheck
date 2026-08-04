"""
Improved Golden Hour Scalping Engine
Phase 1.1: Tighter entry signal filtering for higher Profit Factor

Uses improved order flow analyzer with:
- Requirement of 3+ confirmations
- RSI filtering
- Trend strength validation
- Volume surge filtering (2.0x instead of 1.5x)
- Stricter momentum requirements

Expected improvement: Profit Factor 0.92 → 1.3+
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from adaptive_risk import AdaptiveRiskManager, RiskParams
from market_hours import MarketHourDetector, TradingSession
from order_flow_improved import OrderFlowAnalyzerImproved, OrderFlowSignal
from trade_logger import TradeLogger
from monitoring import MonitoringSystem, AlertLevel
from ring_buffer import RingBuffer, EventBuffer
from ledger_worker import LedgerWorker


@dataclass
class ScalpingSignal:
    """Scalping entry signal"""
    direction: str  # LONG or SHORT
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    position_size: float
    confidence: float
    signal_sources: List[str]
    signal_quality: str
    timestamp: datetime


class GoldenHourScalpingEngineImproved:
    """
    IMPROVED: Adaptive scalping engine with stricter entry filters.
    Target: Improve Profit Factor from 0.92 to 1.3+
    """

    def __init__(
        self,
        symbol: str = "ETHUSDT",
        initial_capital: float = 10000.0,
        session_id: str = "default",
        min_confidence: float = 0.75  # IMPROVED: Raised from 0.70
    ):
        self.logger = logging.getLogger("ScalpingEngineImproved")
        self.symbol = symbol
        self.session_id = session_id
        self.min_confidence = min_confidence

        # Core components - using IMPROVED order flow analyzer
        self.risk_manager = AdaptiveRiskManager(
            initial_capital=initial_capital,
            base_risk_per_trade=0.015,
            kelly_fraction=0.25,
            max_consecutive_losses=3
        )

        self.market_hours = MarketHourDetector()
        # IMPROVED: Using improved order flow analyzer
        self.order_flow = OrderFlowAnalyzerImproved(lookback_periods=50)
        self.trade_logger = TradeLogger(fallback_file="/tmp/neus_trades_improved.jsonl")
        self.monitor = MonitoringSystem()

        # Bifurcated architecture
        self.ring_buffer = RingBuffer(max_size=10000)
        self.event_buffer = EventBuffer(self.ring_buffer)
        self.ledger_worker = LedgerWorker(
            ring_buffer=self.ring_buffer,
            trade_logger=self.trade_logger,
            batch_size=50,
            flush_interval_sec=2.0
        )

        # State
        self.is_running = False
        self.open_positions: Dict[str, Dict] = {}
        self.last_candle = None
        self.volatility_estimate = 0.8

        # Statistics
        self.signals_generated = 0
        self.signals_rejected = 0
        self.high_quality_signals = 0

        self.logger.info(
            f"ScalpingEngineImproved initialized: {symbol}, Capital=${initial_capital}, "
            f"Session={session_id}, MinConfidence={min_confidence}"
        )

    def on_candle(
        self,
        timestamp: datetime,
        open_price: float,
        high: float,
        low: float,
        close: float,
        volume: float,
        atr: float = 0.0
    ) -> Optional[ScalpingSignal]:
        """
        Process incoming candle with IMPROVED filtering.
        Only generates HIGH-QUALITY signals.
        """
        try:
            # Update order flow analyzer
            self.order_flow.add_candle(close, volume, high, low)

            # Estimate volatility
            if atr > 0:
                self.volatility_estimate = (atr / close) * 100

            # Check trading hours
            market_state = self.market_hours.get_market_state(timestamp)
            if not market_state['is_trading_active'] and market_state['is_prime_hour'] is False:
                return None

            # Analyze order flow (IMPROVED version)
            order_flow_signal = self.order_flow.analyze_order_flow(atr)

            # IMPROVED: Stricter filtering
            if order_flow_signal is None:
                self.signals_rejected += 1
                return None

            # IMPROVED: Check confidence threshold
            if order_flow_signal.confidence < self.min_confidence:
                self.signals_rejected += 1
                return None

            # NEW: Track signal quality
            if order_flow_signal.signal_quality == "HIGH":
                self.high_quality_signals += 1

            self.signals_generated += 1

            # Get risk parameters
            risk_params = self.risk_manager.get_risk_parameters(self.volatility_estimate)

            # Create scalping signal
            scalping_signal = self._create_scalping_signal(
                order_flow_signal,
                close,
                risk_params,
                market_state
            )

            if scalping_signal:
                self.logger.info(
                    f"✓ HIGH-QUALITY Signal: {scalping_signal.direction} "
                    f"@ {scalping_signal.entry_price:.2f} "
                    f"(Confidence: {scalping_signal.confidence:.1%}, "
                    f"Quality: {scalping_signal.signal_quality}) "
                    f"Size: ${scalping_signal.position_size:.2f}"
                )

                # Enqueue signal
                self.event_buffer.enqueue_signal(
                    symbol=self.symbol,
                    signal_type="scalping",
                    direction=scalping_signal.direction,
                    confidence=scalping_signal.confidence,
                    agent_id="scalping_engine_improved",
                    session_id=self.session_id,
                    metadata={
                        'market_session': market_state['session'],
                        'volatility': self.volatility_estimate,
                        'sources': scalping_signal.signal_sources,
                        'signal_quality': scalping_signal.signal_quality,
                        'rsi': self.order_flow.get_current_rsi()
                    }
                )

                return scalping_signal

            # Store last candle
            self.last_candle = {
                'timestamp': timestamp,
                'close': close,
                'high': high,
                'low': low,
                'volume': volume,
                'atr': atr
            }

            return None

        except Exception as e:
            self.logger.error(f"Error processing candle: {e}", exc_info=True)
            self.monitor.add_alert(AlertLevel.WARNING, "Candle Processing Error", str(e))
            return None

    def _create_scalping_signal(
        self,
        order_flow_signal: OrderFlowSignal,
        current_price: float,
        risk_params: RiskParams,
        market_state: Dict
    ) -> Optional[ScalpingSignal]:
        """Create scalping signal from order flow signal"""

        # Calculate stop loss and take profits
        stop_loss = current_price - (current_price * risk_params.stop_loss_pct)
        tp1, tp2 = self.risk_manager.get_take_profit_targets(
            current_price, self.volatility_estimate
        )

        # Adjust for direction
        if order_flow_signal.direction == "SHORT":
            stop_loss = current_price + (current_price * risk_params.stop_loss_pct)
            tp1 = current_price * (1.0 - 0.0075)
            tp2 = current_price * (1.0 - 0.012)

        # Position sizing
        position_size = risk_params.position_size

        # IMPROVED: Adjust position size based on signal quality
        if order_flow_signal.signal_quality == "HIGH":
            position_size *= 1.0  # Full size for high-quality signals
        elif order_flow_signal.signal_quality == "MEDIUM":
            position_size *= 0.7  # Reduce to 70% for medium quality
        else:
            position_size *= 0.4  # Only 40% for low quality

        # Adjust for market conditions
        if market_state['is_prime_hour']:
            position_size *= 1.0
        else:
            position_size *= 0.6

        # Confidence calculation
        confidence = min(0.95, order_flow_signal.confidence * market_state.get('volatility_factor', 1.0))

        return ScalpingSignal(
            direction=order_flow_signal.direction,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            position_size=position_size,
            confidence=confidence,
            signal_sources=['order_flow_improved', 'adaptive_risk', 'market_hours'],
            signal_quality=order_flow_signal.signal_quality,
            timestamp=datetime.utcnow()
        )

    def execute_scalp_trade(self, signal: ScalpingSignal) -> bool:
        """Execute scalping trade"""
        try:
            metrics = self.risk_manager.get_metrics()
            if self.risk_manager.should_pause_trading():
                self.logger.warning("Trading paused due to risk limits")
                return False

            if len(self.open_positions) >= 3:
                self.logger.warning("Maximum open positions reached")
                return False

            trade_id = f"{self.symbol}_{signal.timestamp.timestamp()}"
            self.open_positions[trade_id] = {
                'signal': signal,
                'entry_time': signal.timestamp,
                'entry_price': signal.entry_price,
                'position_size': signal.position_size,
                'direction': signal.direction,
                'stop_loss': signal.stop_loss,
                'tp1': signal.take_profit_1,
                'tp2': signal.take_profit_2,
                'pnl': 0.0,
                'tp1_hit': False,
                'tp2_hit': False,
                'signal_quality': signal.signal_quality
            }

            self.logger.info(f"Trade executed: {trade_id} {signal.direction} {signal.position_size:.2f}")
            return True

        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False

    def on_position_update(self, current_price: float, timestamp: datetime):
        """Update open positions and check for exits"""
        closed_trades = []

        for trade_id, position in list(self.open_positions.items()):
            signal = position['signal']
            entry_price = position['entry_price']
            direction = position['direction']

            # Calculate unrealized P&L
            if direction == "LONG":
                pnl = (current_price - entry_price) * position['position_size']
                pnl_pct = (current_price - entry_price) / entry_price
            else:
                pnl = (entry_price - current_price) * position['position_size']
                pnl_pct = (entry_price - current_price) / entry_price

            position['pnl'] = pnl
            position['pnl_pct'] = pnl_pct

            # Check exit conditions
            exit_price = None
            exit_reason = None

            # Stop loss hit
            if direction == "LONG" and current_price <= position['stop_loss']:
                exit_price = position['stop_loss']
                exit_reason = "stop_loss"
            elif direction == "SHORT" and current_price >= position['stop_loss']:
                exit_price = position['stop_loss']
                exit_reason = "stop_loss"

            # Take profit 1 hit
            if not position['tp1_hit']:
                if direction == "LONG" and current_price >= position['tp1']:
                    position['tp1_hit'] = True
                elif direction == "SHORT" and current_price <= position['tp1']:
                    position['tp1_hit'] = True

            # Take profit 2 hit
            if direction == "LONG" and current_price >= position['tp2']:
                exit_price = position['tp2']
                exit_reason = "take_profit_2"
            elif direction == "SHORT" and current_price <= position['tp2']:
                exit_price = position['tp2']
                exit_reason = "take_profit_2"

            # Close trade
            if exit_price:
                self._close_trade(
                    trade_id, position, exit_price, exit_reason, timestamp
                )
                closed_trades.append((trade_id, position, exit_price, exit_reason))

        # Remove closed positions
        for trade_id, _, _, _ in closed_trades:
            del self.open_positions[trade_id]

        self._update_monitoring(current_price, timestamp)

    def _close_trade(
        self,
        trade_id: str,
        position: Dict,
        exit_price: float,
        exit_reason: str,
        timestamp: datetime
    ):
        """Close a trade"""
        pnl = position['pnl']
        pnl_pct = position['pnl_pct']

        # Update risk manager
        self.risk_manager.update_performance(
            pnl=pnl,
            trade_price=exit_price,
            stop_loss=position['stop_loss'],
            take_profit=position['tp2']
        )

        # Enqueue trade
        self.event_buffer.enqueue_trade(
            symbol=self.symbol,
            direction=position['direction'],
            entry_price=position['entry_price'],
            exit_price=exit_price,
            position_size=position['position_size'],
            pnl=pnl,
            pnl_pct=pnl_pct,
            stop_loss=position['stop_loss'],
            take_profit=position['tp2'],
            exit_reason=exit_reason,
            agent_id="scalping_engine_improved",
            session_id=self.session_id
        )

        self.logger.info(
            f"Trade closed: {trade_id} | "
            f"Exit: {exit_reason} @ {exit_price:.2f} | "
            f"PnL: ${pnl:.2f} ({pnl_pct:.2%})"
        )

    def _update_monitoring(self, current_price: float, timestamp: datetime):
        """Update monitoring system"""
        metrics = self.risk_manager.get_metrics()
        metrics['open_positions'] = len(self.open_positions)
        metrics['current_price'] = current_price
        self.monitor.update_metrics(metrics)

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        market_state = self.market_hours.get_market_state()
        risk_metrics = self.risk_manager.get_metrics()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'symbol': self.symbol,
            'market_state': market_state,
            'risk_metrics': risk_metrics,
            'open_positions': len(self.open_positions),
            'volatility_estimate': self.volatility_estimate,
            'signals_generated': self.signals_generated,
            'signals_rejected': self.signals_rejected,
            'high_quality_signals': self.high_quality_signals,
            'rejection_rate': self.signals_rejected / (self.signals_generated + self.signals_rejected) if (self.signals_generated + self.signals_rejected) > 0 else 0
        }

    def start(self):
        """Start the scalping engine"""
        self.is_running = True
        self.ledger_worker.start()
        self.logger.info(f"Improved scalping engine started")

    def stop(self):
        """Stop the scalping engine"""
        self.is_running = False
        self.ledger_worker.stop()
        self.logger.info(f"Improved scalping engine stopped")
        self.trade_logger.close()
