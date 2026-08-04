"""
Bifurcation Architecture Diagnostics
Verifies in-memory execution with background persistence.
"""

import logging
from typing import Dict, List
from datetime import datetime
import time


class BifurcationMonitor:
    """
    Monitor the bifurcated architecture performance.
    Tracks critical path latency and background worker throughput.
    """

    def __init__(self, update_interval_sec: float = 5.0):
        self.logger = logging.getLogger("BifurcationMonitor")
        self.update_interval_sec = update_interval_sec

        # Metrics
        self.metrics = {
            'total_critical_path_calls': 0,
            'total_ring_buffer_enqueues': 0,
            'ring_buffer_drop_count': 0,
            'background_worker_processed': 0,
            'background_worker_errors': 0,
            'start_time': datetime.utcnow()
        }

    def record_critical_path_call(self):
        """Record call in critical path"""
        self.metrics['total_critical_path_calls'] += 1

    def record_enqueue(self, success: bool):
        """Record ring buffer enqueue"""
        if success:
            self.metrics['total_ring_buffer_enqueues'] += 1
        else:
            self.metrics['ring_buffer_drop_count'] += 1

    def sync_worker_stats(self, worker_stats: Dict):
        """Sync stats from background worker"""
        self.metrics['background_worker_processed'] = (
            worker_stats.get('signals_logged', 0) +
            worker_stats.get('trades_logged', 0) +
            worker_stats.get('perf_logged', 0)
        )
        self.metrics['background_worker_errors'] = worker_stats.get('errors', 0)

    def get_latency_analysis(self, ring_buffer, ledger_worker) -> Dict:
        """Analyze critical path latency improvement"""
        return {
            'ring_buffer_size': ring_buffer.size(),
            'ring_buffer_stats': ring_buffer.stats(),
            'worker_stats': ledger_worker.get_stats(),
            'worker_alive': ledger_worker.is_alive(),
            'enqueue_vs_processed_ratio': (
                self.metrics['total_ring_buffer_enqueues'] /
                max(1, self.metrics['background_worker_processed'])
            ),
            'uptime_seconds': (
                datetime.utcnow() - self.metrics['start_time']
            ).total_seconds()
        }

    def print_diagnostics(self, ring_buffer, ledger_worker):
        """Print comprehensive diagnostics"""
        analysis = self.get_latency_analysis(ring_buffer, ledger_worker)

        output = []
        output.append("=" * 70)
        output.append("BIFURCATION ARCHITECTURE DIAGNOSTICS")
        output.append("=" * 70)

        # Critical Path Metrics
        output.append("\n─ CRITICAL PATH (Trading Engine) ─")
        output.append(f"Total calls: {self.metrics['total_critical_path_calls']}")
        output.append(f"Ring buffer enqueues: {self.metrics['total_ring_buffer_enqueues']}")
        output.append(f"Dropped events: {self.metrics['ring_buffer_drop_count']}")
        if self.metrics['total_ring_buffer_enqueues'] > 0:
            drop_rate = (self.metrics['ring_buffer_drop_count'] /
                        self.metrics['total_ring_buffer_enqueues'] * 100)
            output.append(f"Drop rate: {drop_rate:.2f}%")

        # Background Worker Metrics
        output.append("\n─ BACKGROUND WORKER (Persistence) ─")
        output.append(f"Status: {'Running' if analysis['worker_alive'] else 'Stopped'}")
        output.append(f"Events processed: {self.metrics['background_worker_processed']}")
        output.append(f"Errors: {self.metrics['background_worker_errors']}")

        worker_stats = analysis['worker_stats']
        output.append(f"  Signals logged: {worker_stats.get('signals_logged', 0)}")
        output.append(f"  Trades logged: {worker_stats.get('trades_logged', 0)}")
        output.append(f"  Performance snapshots: {worker_stats.get('perf_logged', 0)}")

        # Ring Buffer State
        output.append("\n─ RING BUFFER STATE ─")
        output.append(f"Current queue depth: {analysis['ring_buffer_size']} events")
        rb_stats = analysis['ring_buffer_stats']
        output.append(f"Total enqueued: {rb_stats['total_events']}")
        output.append(f"Capacity: {rb_stats['buffer_capacity']}")
        output.append(f"Enqueue/Process ratio: {analysis['enqueue_vs_processed_ratio']:.2f}x")

        # Efficiency Metrics
        output.append("\n─ EFFICIENCY METRICS ─")
        output.append(f"Uptime: {analysis['uptime_seconds']:.1f} seconds")

        if self.metrics['total_critical_path_calls'] > 0:
            throughput = (self.metrics['total_ring_buffer_enqueues'] /
                         analysis['uptime_seconds'])
            output.append(f"Critical path throughput: {throughput:.1f} calls/sec")

        if self.metrics['background_worker_processed'] > 0:
            worker_throughput = (self.metrics['background_worker_processed'] /
                                analysis['uptime_seconds'])
            output.append(f"Background persistence: {worker_throughput:.1f} events/sec")

        # Architecture Validation
        output.append("\n─ ARCHITECTURE VALIDATION ─")

        # Check 1: Ring buffer not overflowing
        if rb_stats['dropped_events'] == 0:
            output.append("✓ Ring buffer: No overflow")
        else:
            output.append(f"✗ Ring buffer: {rb_stats['dropped_events']} events dropped")

        # Check 2: Background worker catching up
        lag = analysis['enqueue_vs_processed_ratio']
        if lag < 1.5:
            output.append(f"✓ Worker latency: Caught up ({lag:.2f}x)")
        elif lag < 3.0:
            output.append(f"⚠ Worker latency: Slight lag ({lag:.2f}x)")
        else:
            output.append(f"✗ Worker latency: Falling behind ({lag:.2f}x)")

        # Check 3: No worker errors
        if self.metrics['background_worker_errors'] == 0:
            output.append("✓ Worker stability: No errors")
        else:
            output.append(f"✗ Worker stability: {self.metrics['background_worker_errors']} errors")

        # Check 4: Worker is alive
        if analysis['worker_alive']:
            output.append("✓ Worker process: Running")
        else:
            output.append("✗ Worker process: Not running")

        output.append("\n" + "=" * 70)
        print("\n".join(output))

    def export_diagnostics(self, filename: str, ring_buffer, ledger_worker):
        """Export diagnostics to JSON file"""
        import json

        analysis = self.get_latency_analysis(ring_buffer, ledger_worker)
        data = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': self.metrics,
            'analysis': {
                'ring_buffer_size': analysis['ring_buffer_size'],
                'ring_buffer_stats': analysis['ring_buffer_stats'],
                'worker_stats': analysis['worker_stats'],
                'worker_alive': analysis['worker_alive'],
                'enqueue_vs_processed_ratio': analysis['enqueue_vs_processed_ratio']
            }
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.info(f"Diagnostics exported to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to export diagnostics: {e}")


def validate_bifurcation_architecture(scalping_engine) -> bool:
    """
    Validate that bifurcation is correctly implemented.
    Returns True if all checks pass.
    """
    logger = logging.getLogger("BifurcationValidator")

    checks = []

    # Check 1: Ring buffer exists
    if hasattr(scalping_engine, 'ring_buffer'):
        checks.append(("Ring buffer instantiated", True))
    else:
        checks.append(("Ring buffer instantiated", False))

    # Check 2: Event buffer exists
    if hasattr(scalping_engine, 'event_buffer'):
        checks.append(("Event buffer instantiated", True))
    else:
        checks.append(("Event buffer instantiated", False))

    # Check 3: Ledger worker exists
    if hasattr(scalping_engine, 'ledger_worker'):
        checks.append(("Ledger worker instantiated", True))
    else:
        checks.append(("Ledger worker instantiated", False))

    # Check 4: Worker is daemon thread
    if (hasattr(scalping_engine, 'ledger_worker') and
        scalping_engine.ledger_worker.daemon):
        checks.append(("Worker is daemon thread", True))
    else:
        checks.append(("Worker is daemon thread", False))

    # Print results
    print("\n" + "=" * 60)
    print("BIFURCATION ARCHITECTURE VALIDATION")
    print("=" * 60)

    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All bifurcation checks passed")
    else:
        print("\n✗ Some bifurcation checks failed")

    print("=" * 60 + "\n")

    return all_passed
