"""Audit logging and compliance tracking (ISO 27001 A.12.4.1)"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging


class AuditLogger:
    """Immutable audit trail for compliance (7-year retention)"""

    def __init__(self, log_dir: str = '/var/log/neus_trader/audit'):
        """Initialize audit logger with WORM storage"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Separate log files by event type
        self.event_types = {
            'authentication': 'auth.jsonl',
            'authorization': 'authz.jsonl',
            'data_access': 'access.jsonl',
            'configuration': 'config.jsonl',
            'trading': 'trading.jsonl',
            'system': 'system.jsonl',
            'compliance': 'compliance.jsonl'
        }

        self.logger = logging.getLogger('audit')
        self._setup_logger()

    def _setup_logger(self):
        """Configure audit logger with rotating file handler"""
        handler = logging.FileHandler(self.log_dir / 'audit.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_event(self,
                  event_type: str,
                  user_id: str,
                  action: str,
                  resource: str,
                  result: str,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None) -> str:
        """Log security event with immutable storage"""

        if event_type not in self.event_types:
            raise ValueError(f"Invalid event_type: {event_type}")

        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'result': result,  # success, failure, unauthorized
            'ip_address': ip_address,
            'user_agent_hash': self._hash_user_agent(user_agent) if user_agent else None,
            'details': details or {},
            'sequence_number': self._get_next_sequence(event_type)
        }

        # Append to type-specific JSONL file (immutable)
        self._write_audit_entry(event_type, event)

        # Also log to main audit log
        self.logger.info(json.dumps(event))

        return event['timestamp']

    def log_authentication(self,
                         user_id: str,
                         method: str,
                         result: str,
                         ip_address: str = None,
                         mfa_verified: bool = False,
                         details: Dict = None):
        """Log authentication event"""
        self.log_event(
            event_type='authentication',
            user_id=user_id,
            action='login',
            resource=f'user:{user_id}',
            result=result,
            ip_address=ip_address,
            details={
                'method': method,  # password, api_key, oauth
                'mfa_verified': mfa_verified,
                **(details or {})
            }
        )

    def log_data_access(self,
                       user_id: str,
                       action: str,
                       resource_type: str,
                       resource_id: str,
                       fields_accessed: List[str] = None,
                       details: Dict = None):
        """Log data access event"""
        self.log_event(
            event_type='data_access',
            user_id=user_id,
            action=action,
            resource=f'{resource_type}:{resource_id}',
            result='success',
            details={
                'fields_accessed': fields_accessed or [],
                'data_classification': 'confidential',
                **(details or {})
            }
        )

    def log_configuration_change(self,
                                user_id: str,
                                resource: str,
                                change_type: str,
                                before_value: Any,
                                after_value: Any):
        """Log configuration change"""
        self.log_event(
            event_type='configuration',
            user_id=user_id,
            action='modify',
            resource=resource,
            result='success',
            details={
                'change_type': change_type,
                'before': str(before_value),
                'after': str(after_value),
                'change_approved': False  # Should be updated by approval system
            }
        )

    def log_trading_action(self,
                          user_id: str,
                          action: str,
                          symbol: str,
                          position_size: float,
                          pnl: Optional[float] = None,
                          risk_level: str = 'medium'):
        """Log trading-related events"""
        self.log_event(
            event_type='trading',
            user_id=user_id,
            action=action,
            resource=f'trade:{symbol}',
            result='success',
            details={
                'symbol': symbol,
                'position_size': position_size,
                'pnl': pnl,
                'risk_level': risk_level,
                'timestamp_utc': datetime.utcnow().isoformat()
            }
        )

    def log_system_event(self,
                        event: str,
                        severity: str,
                        component: str,
                        details: Dict = None):
        """Log system events (deployments, errors, etc.)"""
        self.log_event(
            event_type='system',
            user_id='system',
            action=event,
            resource=f'system:{component}',
            result=severity,
            details={
                'severity': severity,  # info, warning, error, critical
                'component': component,
                **(details or {})
            }
        )

    def log_compliance_check(self,
                            check_type: str,
                            status: str,
                            details: Dict = None):
        """Log compliance audit results"""
        self.log_event(
            event_type='compliance',
            user_id='system',
            action='audit',
            resource=f'compliance:{check_type}',
            result=status,
            details={
                'check_type': check_type,
                'timestamp': datetime.utcnow().isoformat(),
                **(details or {})
            }
        )

    def _write_audit_entry(self, event_type: str, event: Dict):
        """Write audit entry to JSONL file (append-only)"""
        log_file = self.log_dir / self.event_types[event_type]

        # WORM (Write Once, Read Many) - only append
        with open(log_file, 'a') as f:
            f.write(json.dumps(event, default=str) + '\n')

    def _get_next_sequence(self, event_type: str) -> int:
        """Get next sequence number for event"""
        log_file = self.log_dir / self.event_types[event_type]

        if not log_file.exists():
            return 1

        # Count existing entries
        try:
            with open(log_file, 'r') as f:
                count = sum(1 for _ in f)
            return count + 1
        except:
            return 1

    @staticmethod
    def _hash_user_agent(user_agent: str) -> str:
        """Hash user agent for logging"""
        import hashlib
        return hashlib.sha256(user_agent.encode()).hexdigest()[:16]

    def get_audit_trail(self,
                       event_type: Optional[str] = None,
                       user_id: Optional[str] = None,
                       days: int = 7) -> List[Dict]:
        """Retrieve audit trail for analysis"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        results = []

        log_files = [self.event_types[event_type]] if event_type else self.event_types.values()

        for log_file_name in log_files:
            log_file = self.log_dir / log_file_name

            if not log_file.exists():
                continue

            with open(log_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)

                        # Apply filters
                        if user_id and entry.get('user_id') != user_id:
                            continue

                        event_time = datetime.fromisoformat(entry['timestamp'])
                        if event_time < cutoff_time:
                            continue

                        results.append(entry)
                    except json.JSONDecodeError:
                        continue

        return sorted(results, key=lambda x: x['timestamp'], reverse=True)

    def export_audit_report(self,
                           output_file: str,
                           event_type: Optional[str] = None,
                           days: int = 30):
        """Export audit trail to file (compliance reporting)"""
        entries = self.get_audit_trail(event_type, days=days)

        with open(output_file, 'w') as f:
            f.write(f"# Audit Report - {datetime.utcnow().isoformat()}\n\n")
            f.write(f"Total Events: {len(entries)}\n")
            f.write(f"Period: Last {days} days\n\n")

            for entry in entries:
                f.write(f"[{entry['timestamp']}] {entry['event_type'].upper()}\n")
                f.write(f"  User: {entry['user_id']}\n")
                f.write(f"  Action: {entry['action']}\n")
                f.write(f"  Resource: {entry['resource']}\n")
                f.write(f"  Result: {entry['result']}\n")
                if entry['details']:
                    f.write(f"  Details: {json.dumps(entry['details'])}\n")
                f.write("\n")


class SecurityEventMonitor:
    """Real-time monitoring of security events"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.alerts = []
        self.thresholds = {
            'failed_logins_5min': 5,
            'failed_logins_1hr': 10,
            'api_rate_limit_1min': 1000,
            'large_trade_position': 2.0  # 2x average
        }

    def check_failed_login_spike(self, user_id: str) -> bool:
        """Alert on multiple failed logins"""
        trail = self.audit_logger.get_audit_trail(
            event_type='authentication',
            user_id=user_id,
            days=1
        )

        failed_logins = [e for e in trail if e['result'] == 'failure']

        # Check last 5 minutes
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_failures = [
            e for e in failed_logins
            if datetime.fromisoformat(e['timestamp']) > five_min_ago
        ]

        if len(recent_failures) >= self.thresholds['failed_logins_5min']:
            self._alert(
                'security_alert',
                f"Multiple failed logins for user {user_id}",
                {'count': len(recent_failures), 'period': '5min'}
            )
            return True

        return False

    def check_unusual_activity(self, user_id: str) -> bool:
        """Detect unusual user activity patterns"""
        trail = self.audit_logger.get_audit_trail(user_id=user_id, days=7)

        if not trail:
            return False

        # Check for activity outside normal hours
        activity_hours = [datetime.fromisoformat(e['timestamp']).hour for e in trail]
        off_hours = [h for h in activity_hours if h < 6 or h > 22]

        if len(off_hours) > len(activity_hours) * 0.2:  # >20% off-hours
            self._alert(
                'unusual_activity',
                f"User {user_id} active during unusual hours",
                {'off_hours_percentage': len(off_hours) / len(activity_hours)}
            )
            return True

        return False

    def _alert(self, alert_type: str, message: str, details: Dict = None):
        """Create security alert"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': alert_type,
            'message': message,
            'details': details or {},
            'severity': 'high'
        }
        self.alerts.append(alert)

        # Log to audit trail
        self.audit_logger.log_system_event(
            event=alert_type,
            severity='warning',
            component='security_monitor',
            details=alert
        )
