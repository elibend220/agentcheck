"""
Golden Hour Scalping Engine
Phase 1: MVP with adaptive risk and market hour optimization.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
from dataclasses import dataclass

from adaptive_risk import AdaptiveRiskManager, RiskParams
from market_hours import MarketHourDetector, TradingSession
from order_flow import OrderFlowAnalyzer, OrderFlowSignal
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
    take_profit_1: float  # First target
    take_profit_2: float  # Second target
    position_size: float
    confidence: float
    signal_sources: List[str]  # Which analyzers generated this
    timestamp: datetime


class GoldenHourScalpingEngine:
    """
    Adaptive scalping engine optimized for Golden Hours.
    Target: 40-minute trades capturing 0.75-1.2% moves.
    Strategy: Multi-confirmation entry, aggressive exit on targets.
    """

    def __init__(
        self,
        symbol: str = "ETHUSDT",
        initial_capital: float = 10000.0,
        session_id: str = "default"
    ):
        self.logger = logging.getLogger("ScalpingEngine")
        self.symbol = symbol
        self.session_id = session_id

        # Core components
        self.risk_manager = AdaptiveRiskManager(
            initial_capital=initial_capital,
            base_risk_per_trade=0.015,  # 1.5%
            kelly_fraction=0.25,
            max_consecutive_losses=3
        )

        self.market_hours = MarketHourDetector()
        self.order_flow = OrderFlowAnalyzer(lookback_periods=50)
        self.trade_logger = TradeLogger(fallback_file="/tmp/neus_trades.jsonl")
        self.monitor = MonitoringSystem()

        # Bifurcated architecture: In-memory ring buffer + background worker
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
        self.volatility_estimate = 0.8  # Default 0.8% volatility

        self.logger.info(
            f"ScalpingEngine initialized: {symbol}, Capital=${initial_capital}, "
            f"Session={session_id}"
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
        Process incoming candle and generate signals.
        Main entry point for real-time trading.
        """
        try:
            # Update order flow analyzer
            self.order_flow.add_candle(close, volume, high, low)

            # Estimate volatility from ATR
            if atr > 0:
                self.volatility_estimate = (atr / close) * 100

            # Check if we should be trading
            market_state = self.market_hours.get_market_state(timestamp)
            if not market_state['is_trading_active'] and market_state['is_prime_hour'] is False:
                self.logger.debug("Outside trading hours, skipping analysis")
                return None

            # Analyze order flow
            order_flow_signal = self.order_flow.analyze_order_flow(atr)

            # Get risk parameters
            risk_params = self.risk_manager.get_risk_parameters(self.volatility_estimate)

            # Generate scalping signal if conditions align
            if order_flow_signal and order_flow_signal.confidence >= 0.70:
                scalping_signal = self._create_scalping_signal(
                    order_flow_signal,
                    close,
                    risk_params,
                    market_state
                )

                if scalping_signal:
                    self.logger.info(
                        f"Scalping Signal: {scalping_signal.direction} "
                        f"@ {scalping_signal.entry_price:.2f} "
                        f"(Confidence: {scalping_signal.confidence:.1%}) "
                        f"Size: ${scalping_signal.position_size:.2f}"
                    )

                    # Enqueue signal (non-blocking, memory-only)
                    self.event_buffer.enqueue_signal(
                        symbol=self.symbol,
                        signal_type="scalping",
                        direction=scalping_signal.direction,
                        confidence=scalping_signal.confidence,
                        agent_id="scalping_engine",
                        session_id=self.session_id,
                        metadata={
                            'market_session': market_state['session'],
                            'volatility': self.volatility_estimate,
                            'sources': scalping_signal.signal_sources
                        }
                    )

                    return scalping_signal

            # Store last candle for next analysis
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
            self.monitor.add_alert(
                AlertLevel.WARNING,
                "Candle Processing Error",
                str(e)
            )
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
        tp1, tp2 = self.risk_manager.get_take_profit_targets(current_price, self.volatility_estimate)

        # Adjust for direction
        if order_flow_signal.direction == "SHORT":
            stop_loss = current_price + (current_price * risk_params.stop_loss_pct)
            # For SHORT, flip TP targets
            tp1 = current_price * (1.0 - 0.0075)
            tp2 = current_price * (1.0 - 0.012)

        # Position sizing
        position_size = risk_params.position_size

        # Adjust for market conditions
        if market_state['is_prime_hour']:
            position_size *= 1.0  # Full size during prime hours
        else:
            position_size *= 0.6  # 60% size outside prime hours

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
            signal_sources=['order_flow', 'adaptive_risk', 'market_hours'],
            timestamp=datetime.utcnow()
        )

    def execute_scalp_trade(self, signal: ScalpingSignal) -> bool:
        """Execute scalping trade"""
        try:
            # Check if we should pause trading
            metrics = self.risk_manager.get_metrics()
            if self.risk_manager.should_pause_trading():
                self.logger.warning("Trading paused due to risk limits")
                self.monitor.add_alert(
                    AlertLevel.CRITICAL,
                    "Trading Paused",
                    "Risk limits exceeded, trading paused"
                )
                return False

            # Check position count
            if len(self.open_positions) >= 3:
                self.logger.warning("Maximum open positions reached")
                return False

            # Record opening
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
                'tp2_hit': False
            }

            self.logger.info(f"Trade executed: {trade_id} {signal.direction} {signal.position_size:.2f}")

            return True

        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False

    def on_position_update(self, current_price: float, timestamp: datetime):
        """
        Update open positions, check for exits.
        Call this with every new price update.
        """
        closed_trades = []

        for trade_id, position in list(self.open_positions.items()):
            signal = position['signal']
            entry_price = position['entry_price']
            direction = position['direction']

            # Calculate unrealized P&L
            if direction == "LONG":
                pnl = (current_price - entry_price) * position['position_size']
                pnl_pct = (current_price - entry_price) / entry_price
            else:  # SHORT
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

            # Take profit 1 hit (exit half position)
            if not position['tp1_hit']:
                if direction == "LONG" and current_price >= position['tp1']:
                    position['tp1_hit'] = True
                    # In real system, exit 50% of position
                elif direction == "SHORT" and current_price <= position['tp1']:
                    position['tp1_hit'] = True

            # Take profit 2 hit (exit remaining)
            if direction == "LONG" and current_price >= position['tp2']:
                exit_price = position['tp2']
                exit_reason = "take_profit_2"
            elif direction == "SHORT" and current_price <= position['tp2']:
                exit_price = position['tp2']
                exit_reason = "take_profit_2"

            # Close trade if exit condition met
            if exit_price:
                self._close_trade(
                    trade_id, position, exit_price, exit_reason, timestamp
                )
                closed_trades.append((trade_id, position, exit_price, exit_reason))

        # Remove closed positions
        for trade_id, _, _, _ in closed_trades:
            del self.open_positions[trade_id]

        # Update monitoring
        self._update_monitoring(current_price, timestamp)

    def _close_trade(
        self,
        trade_id: str,
        position: Dict,
        exit_price: float,
        exit_reason: str,
        timestamp: datetime
    ):
        """Close a trade and record in logger"""
        pnl = position['pnl']
        pnl_pct = position['pnl_pct']

        # Update risk manager
        self.risk_manager.update_performance(
            pnl=pnl,
            trade_price=exit_price,
            stop_loss=position['stop_loss'],
            take_profit=position['tp2']
        )

        # Enqueue trade (non-blocking, memory-only)
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
            agent_id="scalping_engine",
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
        metrics['latest_latency_ms'] = 100  # Placeholder

        self.monitor.update_metrics(metrics)

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        market_state = self.market_hours.get_market_state()
        risk_metrics = self.risk_manager.get_metrics()
        monitor_status = self.monitor.get_status_report()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'symbol': self.symbol,
            'market_state': market_state,
            'risk_metrics': risk_metrics,
            'open_positions': len(self.open_positions),
            'monitoring': monitor_status,
            'volatility_estimate': self.volatility_estimate
        }

    def start(self):
        """Start the scalping engine"""
        self.is_running = True
        # Start background ledger worker (critical path unaffected)
        self.ledger_worker.start()
        self.logger.info(f"Scalping engine started with background ledger worker")

    def stop(self):
        """Stop the scalping engine"""
        self.is_running = False
        # Gracefully shutdown background worker (flushes remaining events)
        self.ledger_worker.stop()
        self.logger.info(f"Scalping engine stopped")
        self.trade_logger.close()
