"""Authentication and authorization management (ISO 27001 A.9.2)"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import jwt
import pyotp


class AuthenticationManager:
    """Multi-factor authentication and credential management"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.mfa_window_size = 1  # Allow 1 time window (±30 seconds)
        self.rate_limiter = {}  # user_id -> (attempt_count, timestamp)
        self.failed_login_threshold = 5
        self.rate_limit_window = 900  # 15 minutes

    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """PBKDF2-HMAC-SHA256 password hashing"""
        if salt is None:
            salt = secrets.token_hex(16)

        dk = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations (OWASP recommended)
        )
        return dk.hex(), salt

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        dk, _ = self.hash_password(password, salt)
        return hmac.compare_digest(dk, stored_hash)

    def check_rate_limit(self, user_id: str) -> Tuple[bool, Optional[int]]:
        """Check if user exceeded failed login attempts"""
        now = time.time()

        if user_id in self.rate_limiter:
            count, timestamp = self.rate_limiter[user_id]

            if now - timestamp > self.rate_limit_window:
                # Window expired, reset
                del self.rate_limiter[user_id]
                return True, None

            if count >= self.failed_login_threshold:
                # Account locked, return wait time
                wait_seconds = int(self.rate_limit_window - (now - timestamp))
                return False, wait_seconds

        return True, None

    def record_failed_login(self, user_id: str):
        """Record failed login attempt"""
        now = time.time()

        if user_id in self.rate_limiter:
            count, timestamp = self.rate_limiter[user_id]
            if now - timestamp < self.rate_limit_window:
                self.rate_limiter[user_id] = (count + 1, timestamp)
            else:
                self.rate_limiter[user_id] = (1, now)
        else:
            self.rate_limiter[user_id] = (1, now)

    def clear_failed_logins(self, user_id: str):
        """Clear failed login count on successful auth"""
        if user_id in self.rate_limiter:
            del self.rate_limiter[user_id]

    def setup_mfa(self, user_id: str) -> Tuple[str, str]:
        """Generate MFA secret and QR code provisioning URI"""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name='NEUS Trader'
        )
        return secret, provisioning_uri

    def verify_mfa(self, secret: str, token: str) -> bool:
        """Verify TOTP token (with ±1 window tolerance)"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=self.mfa_window_size)

    def create_api_key(self, user_id: str, name: str, duration_days: int = 365) -> Tuple[str, str]:
        """Generate API key with hash storage"""
        key = secrets.token_urlsafe(32)
        key_hash, salt = self.hash_password(key)

        return key, key_hash  # Client stores key, server stores hash

    def verify_api_key(self, api_key: str, stored_hash: str, salt: str) -> bool:
        """Verify API key against stored hash"""
        return self.verify_password(api_key, stored_hash, salt)


class SessionManager:
    """JWT-based session management"""

    def __init__(self, secret_key: str, algorithm: str = "RS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.active_sessions = {}  # session_id -> metadata

    def create_session_token(
        self,
        user_id: str,
        duration_hours: int = 24,
        ip_address: str = None,
        user_agent: str = None
    ) -> str:
        """Create JWT session token with claims"""
        now = datetime.utcnow()
        expires = now + timedelta(hours=duration_hours)

        payload = {
            'sub': user_id,  # Subject (user ID)
            'iat': int(now.timestamp()),  # Issued at
            'exp': int(expires.timestamp()),  # Expiration
            'nbf': int(now.timestamp()),  # Not before
            'type': 'session',
            'ip_address': ip_address,
            'user_agent_hash': self._hash_user_agent(user_agent) if user_agent else None
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_session_token(
        self,
        token: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Optional[Dict]:
        """Verify JWT token and validate session claims"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate token type
            if payload.get('type') != 'session':
                return None

            # Validate IP address (if available)
            if ip_address and payload.get('ip_address') != ip_address:
                return None

            # Validate user agent
            if user_agent:
                stored_ua_hash = payload.get('user_agent_hash')
                current_ua_hash = self._hash_user_agent(user_agent)
                if stored_ua_hash != current_ua_hash:
                    return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def revoke_session(self, token: str):
        """Add token to blacklist (revocation list)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            session_id = payload.get('session_id', payload.get('sub'))
            exp = payload.get('exp')

            # Store revocation with expiration
            self.active_sessions[session_id] = {
                'revoked_at': datetime.utcnow().isoformat(),
                'expires_at': datetime.fromtimestamp(exp).isoformat()
            }
        except jwt.InvalidTokenError:
            pass

    def is_session_revoked(self, token: str) -> bool:
        """Check if session token is revoked"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            session_id = payload.get('session_id', payload.get('sub'))
            return session_id in self.active_sessions
        except jwt.InvalidTokenError:
            return True

    @staticmethod
    def _hash_user_agent(user_agent: str) -> str:
        """Hash user agent for session binding"""
        return hashlib.sha256(user_agent.encode()).hexdigest()


class RoleBasedAccessControl:
    """RBAC implementation for authorization"""

    ROLES = {
        'admin': {
            'permissions': [
                'user:manage',
                'trade:execute',
                'trade:view_all',
                'config:modify',
                'audit:view',
                'risk:override'
            ]
        },
        'trader': {
            'permissions': [
                'trade:execute',
                'trade:view_own',
                'config:modify_own',
                'audit:view_own'
            ]
        },
        'analyst': {
            'permissions': [
                'trade:view_all',
                'backtest:view',
                'performance:analyze'
            ]
        },
        'viewer': {
            'permissions': [
                'audit:view',
                'performance:view'
            ]
        }
    }

    def __init__(self):
        self.user_roles = {}  # user_id -> [roles]

    def assign_role(self, user_id: str, role: str) -> bool:
        """Assign role to user"""
        if role not in self.ROLES:
            return False

        if user_id not in self.user_roles:
            self.user_roles[user_id] = []

        if role not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role)

        return True

    def has_permission(self, user_id: str, required_permission: str) -> bool:
        """Check if user has required permission"""
        if user_id not in self.user_roles:
            return False

        for role in self.user_roles[user_id]:
            if role in self.ROLES:
                if required_permission in self.ROLES[role]['permissions']:
                    return True

        return False

    def get_user_permissions(self, user_id: str) -> set:
        """Get all permissions for user"""
        permissions = set()

        if user_id in self.user_roles:
            for role in self.user_roles[user_id]:
                if role in self.ROLES:
                    permissions.update(self.ROLES[role]['permissions'])

        return permissions
