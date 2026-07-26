"""
Real-time Monitoring and Alerting System
Tracks trading performance and triggers alerts for anomalies.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert:
    """Single alert event"""

    def __init__(self, level: AlertLevel, title: str, message: str, metadata: Dict = None):
        self.level = level
        self.title = title
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

    def __str__(self):
        return f"[{self.timestamp.isoformat()}] {self.level.value.upper()}: {self.title} - {self.message}"


class MonitoringSystem:
    """
    Real-time monitoring of trading system.
    Detects anomalies and generates alerts.
    """

    def __init__(self, alert_buffer_size: int = 1000):
        self.logger = logging.getLogger("MonitoringSystem")
        self.alerts: List[Alert] = []
        self.alert_buffer_size = alert_buffer_size

        # Thresholds for alerts
        self.thresholds = {
            'drawdown_warning': 10.0,  # 10%
            'drawdown_critical': 20.0,  # 20%
            'consecutive_losses_warning': 3,
            'consecutive_losses_critical': 5,
            'win_rate_warning': 0.40,  # 40%
            'position_error_threshold': 0.05,  # 5%
            'latency_warning_ms': 500,
            'latency_critical_ms': 2000
        }

        # Current metrics
        self.current_metrics: Dict = {}

    def update_metrics(self, metrics: Dict):
        """Update current trading metrics"""
        self.current_metrics = metrics

        # Run alert checks
        self._check_drawdown(metrics)
        self._check_consecutive_losses(metrics)
        self._check_win_rate(metrics)
        self._check_position_count(metrics)
        self._check_latency(metrics)

    def _check_drawdown(self, metrics: Dict):
        """Check drawdown levels"""
        drawdown = metrics.get('drawdown_pct', 0.0)

        if drawdown < -self.thresholds['drawdown_critical']:
            self.add_alert(
                AlertLevel.CRITICAL,
                "Critical Drawdown",
                f"Drawdown reached {drawdown:.1f}%, exceeds {self.thresholds['drawdown_critical']:.1f}% limit",
                {'drawdown': drawdown}
            )
        elif drawdown < -self.thresholds['drawdown_warning']:
            self.add_alert(
                AlertLevel.WARNING,
                "Significant Drawdown",
                f"Drawdown at {drawdown:.1f}%, caution recommended",
                {'drawdown': drawdown}
            )

    def _check_consecutive_losses(self, metrics: Dict):
        """Check consecutive losses"""
        losses = metrics.get('consecutive_losses', 0)

        if losses >= self.thresholds['consecutive_losses_critical']:
            self.add_alert(
                AlertLevel.CRITICAL,
                "Excessive Losses",
                f"{losses} consecutive losses, trading pause recommended",
                {'consecutive_losses': losses}
            )
        elif losses >= self.thresholds['consecutive_losses_warning']:
            self.add_alert(
                AlertLevel.WARNING,
                "Consecutive Losses",
                f"{losses} losses in a row, reduce position size",
                {'consecutive_losses': losses}
            )

    def _check_win_rate(self, metrics: Dict):
        """Check win rate"""
        win_rate = metrics.get('win_rate', 0.5)
        total_trades = metrics.get('total_trades', 0)

        # Only check if sufficient trades
        if total_trades < 10:
            return

        if win_rate < self.thresholds['win_rate_warning']:
            self.add_alert(
                AlertLevel.WARNING,
                "Low Win Rate",
                f"Win rate {win_rate:.1%} after {total_trades} trades, review strategy",
                {'win_rate': win_rate, 'total_trades': total_trades}
            )

    def _check_position_count(self, metrics: Dict):
        """Check open position count"""
        open_positions = metrics.get('open_positions', 0)
        max_positions = metrics.get('max_positions', 3)

        if open_positions >= max_positions:
            self.add_alert(
                AlertLevel.WARNING,
                "Max Positions Reached",
                f"Open positions ({open_positions}) at maximum ({max_positions})",
                {'open_positions': open_positions, 'max_positions': max_positions}
            )

    def _check_latency(self, metrics: Dict):
        """Check execution latency"""
        latency_ms = metrics.get('latest_latency_ms', 0)

        if latency_ms > self.thresholds['latency_critical_ms']:
            self.add_alert(
                AlertLevel.CRITICAL,
                "High Latency",
                f"Execution latency {latency_ms}ms exceeds {self.thresholds['latency_critical_ms']}ms",
                {'latency_ms': latency_ms}
            )
        elif latency_ms > self.thresholds['latency_warning_ms']:
            self.add_alert(
                AlertLevel.WARNING,
                "Elevated Latency",
                f"Execution latency {latency_ms}ms above normal",
                {'latency_ms': latency_ms}
            )

    def add_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict = None):
        """Add an alert"""
        alert = Alert(level, title, message, metadata)
        self.alerts.append(alert)

        # Log appropriately
        if level == AlertLevel.CRITICAL:
            self.logger.critical(str(alert))
        elif level == AlertLevel.WARNING:
            self.logger.warning(str(alert))
        else:
            self.logger.info(str(alert))

        # Trim buffer
        if len(self.alerts) > self.alert_buffer_size:
            self.alerts = self.alerts[-self.alert_buffer_size:]

    def get_recent_alerts(self, level: Optional[AlertLevel] = None, minutes: int = 60) -> List[Alert]:
        """Get recent alerts, optionally filtered by level"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        filtered = [a for a in self.alerts if a.timestamp > cutoff]

        if level:
            filtered = [a for a in filtered if a.level == level]

        return filtered

    def get_critical_alerts(self) -> List[Alert]:
        """Get all critical alerts from last hour"""
        return self.get_recent_alerts(level=AlertLevel.CRITICAL, minutes=60)

    def get_status_report(self) -> Dict:
        """Get system status report"""
        critical = self.get_critical_alerts()
        warnings = self.get_recent_alerts(level=AlertLevel.WARNING, minutes=60)

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'current_metrics': self.current_metrics,
            'critical_alerts': len(critical),
            'warning_alerts': len(warnings),
            'recent_critical': [
                {'title': a.title, 'message': a.message, 'time': a.timestamp.isoformat()}
                for a in critical[-5:]  # Last 5
            ],
            'recent_warnings': [
                {'title': a.title, 'message': a.message, 'time': a.timestamp.isoformat()}
                for a in warnings[-5:]  # Last 5
            ],
            'health': 'CRITICAL' if critical else 'WARNING' if warnings else 'HEALTHY'
        }

    def export_alerts_json(self, filename: str):
        """Export alerts to JSON for analysis"""
        import json

        try:
            data = [
                {
                    'timestamp': a.timestamp.isoformat(),
                    'level': a.level.value,
                    'title': a.title,
                    'message': a.message,
                    'metadata': a.metadata
                }
                for a in self.alerts
            ]

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Exported {len(self.alerts)} alerts to {filename}")

        except Exception as e:
            self.logger.error(f"Failed to export alerts: {e}")


class DashboardRenderer:
    """Simple text-based dashboard for monitoring"""

    @staticmethod
    def render_status(monitor_system: MonitoringSystem) -> str:
        """Render text-based status dashboard"""
        report = monitor_system.get_status_report()
        metrics = report['current_metrics']

        output = []
        output.append("=" * 70)
        output.append("NEUS_TRADER MONITORING DASHBOARD")
        output.append("=" * 70)

        # Status section
        health = report['health']
        color = "🔴" if health == "CRITICAL" else "🟡" if health == "WARNING" else "🟢"
        output.append(f"\n{color} System Status: {health}\n")

        # Metrics section
        output.append("─ TRADING METRICS ─")
        output.append(f"Capital: ${metrics.get('capital', 0):,.2f}")
        output.append(f"Drawdown: {metrics.get('drawdown_pct', 0):.2f}%")
        output.append(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
        output.append(f"Trades: {metrics.get('total_trades', 0)}")
        output.append(f"Consecutive Losses: {metrics.get('consecutive_losses', 0)}")

        # Alerts section
        if report['recent_critical']:
            output.append("\n─ 🔴 CRITICAL ALERTS ─")
            for alert in report['recent_critical']:
                output.append(f"  ⚠️  {alert['title']}: {alert['message']}")

        if report['recent_warnings']:
            output.append("\n─ 🟡 WARNINGS ─")
            for alert in report['recent_warnings'][:3]:  # Show top 3
                output.append(f"  ⚠️  {alert['title']}")

        output.append("\n" + "=" * 70)

        return "\n".join(output)
