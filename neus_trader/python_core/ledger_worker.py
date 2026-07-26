"""
Ledger Background Worker
Asynchronously persists trading events from ring buffer to disk/database.
Runs in separate thread, never blocks critical execution path.
"""

import logging
import threading
import time
from typing import Optional, List
from queue import Queue, Empty

from ring_buffer import RingBuffer, EventBuffer, TradingEvent, EventType
from trade_logger import TradeLogger


class LedgerWorker(threading.Thread):
    """
    Background worker thread that drains RingBuffer and persists to storage.
    Isolated from critical trading path.
    """

    def __init__(
        self,
        ring_buffer: RingBuffer,
        trade_logger: TradeLogger,
        batch_size: int = 50,
        flush_interval_sec: float = 2.0,
        daemon: bool = True
    ):
        """
        Args:
            ring_buffer: RingBuffer to drain events from
            trade_logger: TradeLogger for persistent storage
            batch_size: Events to process per iteration
            flush_interval_sec: Minimum time between flushes
            daemon: Run as daemon thread (background)
        """
        super().__init__(daemon=daemon)
        self.logger = logging.getLogger("LedgerWorker")

        self.ring_buffer = ring_buffer
        self.trade_logger = trade_logger
        self.batch_size = batch_size
        self.flush_interval_sec = flush_interval_sec

        # Control signals
        self.stop_event = threading.Event()
        self.stats = {
            'signals_logged': 0,
            'trades_logged': 0,
            'perf_logged': 0,
            'errors': 0,
            'last_flush_time': time.time()
        }
        self.stats_lock = threading.Lock()

        self.logger.info(
            f"LedgerWorker initialized: batch_size={batch_size}, "
            f"flush_interval={flush_interval_sec}s"
        )

    def run(self):
        """Main worker loop (runs in background thread)"""
        self.logger.info("LedgerWorker started")

        try:
            while not self.stop_event.is_set():
                self._process_batch()
                time.sleep(0.01)  # Small sleep to prevent busy-waiting

        except Exception as e:
            self.logger.error(f"LedgerWorker crashed: {e}", exc_info=True)
        finally:
            self.logger.info("LedgerWorker stopping...")
            self._flush_remaining()
            self.logger.info("LedgerWorker stopped")

    def _process_batch(self):
        """Process a batch of events from ring buffer"""
        events = self.ring_buffer.dequeue_batch(self.batch_size)

        if not events:
            return

        for event in events:
            self._process_event(event)

        # Update stats
        with self.stats_lock:
            self.stats['last_flush_time'] = time.time()

    def _process_event(self, event: TradingEvent):
        """Process a single event"""
        try:
            if event.event_type == EventType.SIGNAL:
                self._log_signal(event)
            elif event.event_type == EventType.TRADE:
                self._log_trade(event)
            elif event.event_type == EventType.PERFORMANCE:
                self._log_performance(event)
            else:
                self.logger.warning(f"Unknown event type: {event.event_type}")

        except Exception as e:
            self.logger.error(f"Error processing event: {e}")
            with self.stats_lock:
                self.stats['errors'] += 1

    def _log_signal(self, event: TradingEvent):
        """Persist signal event"""
        data = event.data

        self.trade_logger.log_signal(
            symbol=data['symbol'],
            signal_type=data['signal_type'],
            direction=data['direction'],
            confidence=data['confidence'],
            agent_id=data['agent_id'],
            session_id=data['session_id'],
            metadata=data.get('metadata', {})
        )

        with self.stats_lock:
            self.stats['signals_logged'] += 1

    def _log_trade(self, event: TradingEvent):
        """Persist trade event"""
        data = event.data

        self.trade_logger.log_trade(
            symbol=data['symbol'],
            direction=data['direction'],
            entry_price=data['entry_price'],
            exit_price=data['exit_price'],
            position_size=data['position_size'],
            pnl=data['pnl'],
            pnl_pct=data['pnl_pct'],
            stop_loss=data['stop_loss'],
            take_profit=data['take_profit'],
            exit_reason=data['exit_reason'],
            agent_id=data['agent_id'],
            session_id=data['session_id'],
            metadata=data.get('metadata', {})
        )

        with self.stats_lock:
            self.stats['trades_logged'] += 1

    def _log_performance(self, event: TradingEvent):
        """Persist performance event"""
        data = event.data

        self.trade_logger.log_performance(
            capital=data['capital'],
            drawdown_pct=data['drawdown_pct'],
            win_rate=data['win_rate'],
            total_trades=data['total_trades'],
            session_id=data['session_id'],
            market_session=data['market_session'],
            metadata=data.get('metadata', {})
        )

        with self.stats_lock:
            self.stats['perf_logged'] += 1

    def _flush_remaining(self):
        """Drain all remaining events on shutdown"""
        self.logger.info("Flushing remaining events...")

        remaining = self.ring_buffer.dequeue_all()
        self.logger.info(f"Flushing {len(remaining)} events")

        for event in remaining:
            self._process_event(event)

        self.logger.info(f"Flush complete: {len(remaining)} events persisted")

    def get_stats(self) -> dict:
        """Get worker statistics"""
        with self.stats_lock:
            return dict(self.stats)

    def get_stats_string(self) -> str:
        """Get human-readable stats"""
        s = self.get_stats()
        return (
            f"LedgerWorker: {s['signals_logged']} signals, "
            f"{s['trades_logged']} trades, "
            f"{s['perf_logged']} perf, "
            f"{s['errors']} errors"
        )

    def stop(self):
        """Signal worker to stop (graceful shutdown)"""
        self.logger.info("Stopping LedgerWorker...")
        self.stop_event.set()
        self.join(timeout=5.0)

        if self.is_alive():
            self.logger.error("LedgerWorker did not stop gracefully")
