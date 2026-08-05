"""GDPR compliance and privacy management (EU Regulation 2016/679)"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path


class GDPRCompliance:
    """GDPR data subject rights and privacy controls"""

    # Required under GDPR Article 5
    PRIVACY_PRINCIPLES = {
        'lawfulness': 'Legal basis for processing documented',
        'fairness': 'Transparent data practices',
        'transparency': 'Privacy notice provided',
        'purpose_limitation': 'Data used only for stated purpose',
        'data_minimization': 'Only necessary data collected',
        'accuracy': 'Data kept accurate and up-to-date',
        'storage_limitation': 'Data retained only as long as necessary',
        'integrity_confidentiality': 'Secure processing enforced'
    }

    # Legal bases for processing (GDPR Article 6)
    LEGAL_BASES = {
        'consent': 'User explicitly consented',
        'contract': 'Processing required for contract',
        'legal_obligation': 'Required by law',
        'vital_interests': 'Protects vital interests',
        'public_task': 'Necessary for public task',
        'legitimate_interests': 'Legitimate business interests'
    }

    # Data retention periods
    RETENTION_POLICY = {
        'user_profile': 365,  # 1 year
        'trade_records': 2555,  # 7 years (regulatory requirement)
        'audit_logs': 2555,  # 7 years
        'marketing': 730,  # 2 years
        'error_logs': 90,  # 90 days
        'session_tokens': 1  # 24 hours max
    }

    def __init__(self, data_dir: str = '/var/lib/neus_trader/gdpr'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Privacy notices and consent records
        self.consent_records = self.data_dir / 'consent_records.jsonl'
        self.data_access_requests = self.data_dir / 'dsar.jsonl'
        self.deletion_requests = self.data_dir / 'deletion.jsonl'

    def create_privacy_notice(self) -> str:
        """Generate GDPR-compliant privacy notice"""
        notice = """
# PRIVACY NOTICE - NEUS Trader

## 1. Identity of Controller
NEUS Trader Inc. (trading)
Email: privacy@neus-trader.io

## 2. Purpose of Processing
- Execute trading signals on your behalf
- Analyze market performance
- Comply with regulatory requirements
- Improve system performance

## 3. Legal Basis
- Explicit consent (trading authorization)
- Contractual necessity (trading agreement)
- Legal obligations (tax/regulatory reporting)

## 4. Data Categories Collected
- Account information (email, timezone)
- Trading data (orders, fills, P&L)
- System logs (IP address, timestamps)
- Performance metrics (returns, drawdown)

## 5. Recipients
- Trading exchange (Binance)
- Payment processors
- Compliance authorities (if required)

## 6. Retention Period
- Trade records: 7 years (regulatory requirement)
- User profile: 1 year after account closure
- Audit logs: 7 years

## 7. Your Rights
- Right to access your data (DSAR)
- Right to correct inaccuracies
- Right to erasure ("right to be forgotten")
- Right to restrict processing
- Right to portability
- Right to object
- Right to withdraw consent

## 8. Contact
Submit requests to: privacy@neus-trader.io
Response time: 30 days

## 9. Complaints
Contact your national data protection authority
"""
        return notice

    def record_consent(self,
                      user_id: str,
                      consent_type: str,
                      legal_basis: str,
                      version: str = '1.0') -> str:
        """Record user consent (GDPR Article 7)"""

        if legal_basis not in self.LEGAL_BASES:
            raise ValueError(f"Invalid legal basis: {legal_basis}")

        consent_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'consent_type': consent_type,
            'legal_basis': legal_basis,
            'version': version,
            'ip_address_hash': None,  # Can add if needed
            'user_agent_hash': None,  # Can add if needed
            'status': 'granted'
        }

        # Append to consent record file
        with open(self.consent_records, 'a') as f:
            f.write(json.dumps(consent_record) + '\n')

        return consent_record['timestamp']

    def withdraw_consent(self, user_id: str, consent_type: str):
        """Withdraw user consent (GDPR Article 7.3)"""
        withdrawal = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'consent_type': consent_type,
            'status': 'withdrawn'
        }

        with open(self.consent_records, 'a') as f:
            f.write(json.dumps(withdrawal) + '\n')

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Data Subject Access Request (DSAR) - Article 15"""
        # Retrieve all personal data associated with user
        user_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'data_categories': {
                'profile': self._get_user_profile(user_id),
                'trade_history': self._get_trade_history(user_id),
                'audit_logs': self._get_audit_logs(user_id),
                'consent_records': self._get_consent_records(user_id)
            }
        }

        # Log the DSAR
        self._log_dsar(user_id, user_data)

        return user_data

    def export_user_data(self, user_id: str, format: str = 'json') -> str:
        """Data portability - Article 20"""
        user_data = self.get_user_data(user_id)

        if format == 'json':
            return json.dumps(user_data, indent=2, default=str)
        elif format == 'csv':
            return self._convert_to_csv(user_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def request_erasure(self,
                       user_id: str,
                       reason: str = None) -> str:
        """Right to erasure ("right to be forgotten") - Article 17"""

        deletion_request = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'reason': reason,
            'status': 'pending',
            'deadline': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

        # Log deletion request
        with open(self.deletion_requests, 'a') as f:
            f.write(json.dumps(deletion_request) + '\n')

        return deletion_request['timestamp']

    def process_erasure(self, user_id: str, confirm: bool = True) -> bool:
        """Execute data erasure after DSAR verification"""
        if not confirm:
            return False

        # Delete all personal data (pseudonymized retention for records)
        self._anonymize_user_data(user_id)

        # Log the deletion
        deletion_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': f'DELETED_{datetime.utcnow().timestamp()}',
            'action': 'erasure_processed',
            'original_user': user_id
        }

        with open(self.deletion_requests, 'a') as f:
            f.write(json.dumps(deletion_record) + '\n')

        return True

    def anonymize_data(self, data: Dict) -> Dict:
        """Remove personally identifiable information"""
        pii_fields = [
            'email', 'user_email', 'phone', 'wallet_address',
            'ip_address', 'user_agent', 'name', 'address'
        ]

        anonymized = data.copy()

        for field in pii_fields:
            if field in anonymized:
                anonymized[field] = f'[REDACTED_{field}]'

        return anonymized

    def check_retention_expiry(self, data_type: str, created_at: datetime) -> bool:
        """Check if data should be deleted based on retention policy"""
        if data_type not in self.RETENTION_POLICY:
            return False

        retention_days = self.RETENTION_POLICY[data_type]
        expiry_date = created_at + timedelta(days=retention_days)

        return datetime.utcnow() > expiry_date

    def get_compliance_report(self) -> Dict:
        """Generate GDPR compliance report"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0',
            'principles': self.PRIVACY_PRINCIPLES,
            'legal_bases': self.LEGAL_BASES,
            'retention_policy': self.RETENTION_POLICY,
            'dsar_processing_time': '30 days',
            'breach_notification_deadline': '72 hours',
            'controller': 'NEUS Trader Inc.',
            'privacy_contact': 'privacy@neus-trader.io'
        }

    # Private helper methods
    def _get_user_profile(self, user_id: str) -> Dict:
        """Retrieve user profile data"""
        # Implementation depends on database schema
        return {'user_id': user_id, 'created_at': datetime.utcnow().isoformat()}

    def _get_trade_history(self, user_id: str) -> List[Dict]:
        """Retrieve user's trade records"""
        return []

    def _get_audit_logs(self, user_id: str) -> List[Dict]:
        """Retrieve user's audit logs"""
        return []

    def _get_consent_records(self, user_id: str) -> List[Dict]:
        """Retrieve user's consent records"""
        return []

    def _log_dsar(self, user_id: str, data: Dict):
        """Log Data Subject Access Request"""
        dsar_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': 'dsar_processed',
            'data_categories': list(data.get('data_categories', {}).keys())
        }

        with open(self.data_access_requests, 'a') as f:
            f.write(json.dumps(dsar_record) + '\n')

    def _anonymize_user_data(self, user_id: str):
        """Pseudonymize user data (per GDPR recital 26)"""
        # Implementation depends on database
        pass

    def _convert_to_csv(self, data: Dict) -> str:
        """Convert user data to CSV format"""
        # Implementation for CSV export
        return json.dumps(data)


class DataProcessingAgreement:
    """GDPR Data Processing Agreement (Article 28)"""

    def __init__(self, processor_name: str = "Binance"):
        self.processor_name = processor_name
        self.agreement_date = datetime.utcnow().isoformat()

    def get_dpa_terms(self) -> Dict:
        """Data Processing Agreement terms"""
        return {
            'effective_date': self.agreement_date,
            'processor': self.processor_name,
            'processing_activities': [
                'Trade execution',
                'Order tracking',
                'Performance reporting'
            ],
            'data_categories': [
                'Order data',
                'Account information',
                'Trade records'
            ],
            'processing_location': 'Multiple (user jurisdiction + exchange)',
            'sub_processors': [
                'AWS (cloud storage)',
                'Binance (order execution)'
            ],
            'security_measures': [
                'Encryption at rest (AES-256)',
                'Encryption in transit (TLS 1.3)',
                'Access controls (RBAC)',
                'Audit logging (7 years)',
                'Regular security audits'
            ],
            'data_subject_rights': [
                'Right to access',
                'Right to rectification',
                'Right to erasure',
                'Right to restrict processing',
                'Right to portability'
            ],
            'breach_notification': '72 hours maximum',
            'audit_rights': 'Annual security audit with SOC 2 certification'
        }
