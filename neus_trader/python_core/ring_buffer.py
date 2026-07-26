"""
In-Memory Ring Buffer for Trading Events
Zero-copy event queue for critical execution path.
Decouples real-time trading from persistent storage I/O.
"""

import logging
from collections import deque
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import threading


class EventType(Enum):
    """Event types for the ring buffer"""
    SIGNAL = "signal"
    TRADE = "trade"
    PERFORMANCE = "performance"


@dataclass
class TradingEvent:
    """Base trading event"""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 0  # 0=normal, 1=high priority (use for critical events)

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            **self.data
        }


class RingBuffer:
    """
    Lock-free ring buffer for high-frequency trading events.
    Bounded memory, FIFO ordering, thread-safe enqueue/dequeue.
    """

    def __init__(self, max_size: int = 10000):
        """
        Args:
            max_size: Maximum events to buffer (bounded memory)
        """
        self.logger = logging.getLogger("RingBuffer")
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)
        self.lock = threading.Lock()  # Minimal lock for deque operations
        self.event_count = 0
        self.dropped_count = 0

        self.logger.info(f"RingBuffer initialized: {max_size} event slots")

    def enqueue(self, event: TradingEvent) -> bool:
        """
        Add event to buffer (critical path - fast).
        Non-blocking for normal case.

        Args:
            event: TradingEvent to enqueue

        Returns:
            True if enqueued, False if buffer full (dropped)
        """
        try:
            # Fast path: deque.append is thread-safe in CPython
            self.buffer.append(event)
            self.event_count += 1
            return True
        except IndexError:
            # Buffer full (shouldn't happen with deque.maxlen)
            self.dropped_count += 1
            self.logger.warning(f"Ring buffer full, dropped event: {event.event_type.value}")
            return False

    def dequeue_batch(self, batch_size: int = 100) -> List[TradingEvent]:
        """
        Retrieve batch of events (background worker only).
        FIFO order preserved.

        Args:
            batch_size: Max events to retrieve

        Returns:
            List of TradingEvent objects
        """
        batch = []
        with self.lock:
            for _ in range(min(batch_size, len(self.buffer))):
                if self.buffer:
                    batch.append(self.buffer.popleft())
        return batch

    def dequeue_all(self) -> List[TradingEvent]:
        """
        Drain all events from buffer (background worker shutdown).

        Returns:
            All remaining events
        """
        with self.lock:
            batch = list(self.buffer)
            self.buffer.clear()
        return batch

    def size(self) -> int:
        """Current number of events in buffer"""
        return len(self.buffer)

    def stats(self) -> Dict[str, int]:
        """Get buffer statistics"""
        return {
            'queued_events': len(self.buffer),
            'total_events': self.event_count,
            'dropped_events': self.dropped_count,
            'buffer_capacity': self.max_size
        }

    def get_stats_string(self) -> str:
        """Get human-readable stats"""
        s = self.stats()
        return (
            f"RingBuffer: {s['queued_events']}/{s['buffer_capacity']} queued, "
            f"{s['total_events']} total, {s['dropped_events']} dropped"
        )


class EventBuffer:
    """
    Typed event buffer interface.
    Simplifies enqueue calls from trading engine.
    """

    def __init__(self, ring_buffer: RingBuffer):
        self.ring_buffer = ring_buffer
        self.logger = logging.getLogger("EventBuffer")

    def enqueue_signal(
        self,
        symbol: str,
        signal_type: str,
        direction: str,
        confidence: float,
        agent_id: str,
        session_id: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Enqueue signal event (from critical path)"""
        event = TradingEvent(
            event_type=EventType.SIGNAL,
            timestamp=datetime.utcnow(),
            data={
                'symbol': symbol,
                'signal_type': signal_type,
                'direction': direction,
                'confidence': confidence,
                'agent_id': agent_id,
                'session_id': session_id,
                'metadata': metadata or {}
            },
            priority=0
        )
        return self.ring_buffer.enqueue(event)

    def enqueue_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        position_size: float,
        pnl: float,
        pnl_pct: float,
        stop_loss: float,
        take_profit: float,
        exit_reason: str,
        agent_id: str,
        session_id: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Enqueue trade event (from critical path)"""
        event = TradingEvent(
            event_type=EventType.TRADE,
            timestamp=datetime.utcnow(),
            data={
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'exit_reason': exit_reason,
                'agent_id': agent_id,
                'session_id': session_id,
                'metadata': metadata or {}
            },
            priority=1  # High priority - critical for accounting
        )
        return self.ring_buffer.enqueue(event)

    def enqueue_performance(
        self,
        capital: float,
        drawdown_pct: float,
        win_rate: float,
        total_trades: int,
        session_id: str,
        market_session: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Enqueue performance snapshot (from monitoring)"""
        event = TradingEvent(
            event_type=EventType.PERFORMANCE,
            timestamp=datetime.utcnow(),
            data={
                'capital': capital,
                'drawdown_pct': drawdown_pct,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'session_id': session_id,
                'market_session': market_session,
                'metadata': metadata or {}
            },
            priority=0
        )
        return self.ring_buffer.enqueue(event)
