"""Data encryption and secure transport (ISO 27001 A.10.1)"""

import os
import ssl
import certifi
from datetime import datetime
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64


class DataEncryption:
    """AES-based encryption for sensitive data"""

    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption with master key"""
        if master_key is None:
            master_key = os.environ.get('ENCRYPTION_MASTER_KEY')

        if not master_key:
            raise ValueError("ENCRYPTION_MASTER_KEY required")

        self.master_key = master_key
        self.key_version = 1
        self.pii_fields = {
            'user_email',
            'wallet_address',
            'phone_number',
            'api_key',
            'secret_key'
        }

    def _derive_key(self, salt: bytes, key_version: int = None) -> bytes:
        """Derive encryption key using PBKDF2-HMAC-SHA256"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,  # OWASP recommended
            backend=default_backend()
        )
        key_material = self.master_key.encode('utf-8')
        derived_key = kdf.derive(key_material)
        return base64.urlsafe_b64encode(derived_key)

    def encrypt_field(self, value: str, field_name: str = None) -> str:
        """Encrypt sensitive field"""
        if value is None:
            return None

        salt = os.urandom(16)
        derived_key = self._derive_key(salt)

        cipher = Fernet(derived_key)
        encrypted = cipher.encrypt(value.encode('utf-8'))

        # Format: key_version:salt:encrypted:timestamp
        timestamp = datetime.utcnow().isoformat()
        result = f"{self.key_version}:{base64.b64encode(salt).decode()}:{encrypted.decode()}:{timestamp}"

        return result

    def decrypt_field(self, encrypted_value: str) -> Optional[str]:
        """Decrypt sensitive field"""
        if not encrypted_value or ':' not in encrypted_value:
            return None

        try:
            parts = encrypted_value.split(':')
            if len(parts) < 3:
                return None

            key_version = int(parts[0])
            salt = base64.b64decode(parts[1])
            encrypted_data = parts[2]

            # Verify key version matches (for key rotation)
            if key_version != self.key_version:
                raise ValueError("Encrypted with different key version")

            derived_key = self._derive_key(salt, key_version)
            cipher = Fernet(derived_key)
            decrypted = cipher.decrypt(encrypted_data.encode())

            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_database_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Selectively encrypt PII fields in record"""
        encrypted_record = record.copy()

        for field_name, value in record.items():
            if field_name in self.pii_fields and value:
                encrypted_record[field_name] = self.encrypt_field(value, field_name)

        # Add encryption metadata
        encrypted_record['_encryption_version'] = self.key_version
        encrypted_record['_encrypted_at'] = datetime.utcnow().isoformat()

        return encrypted_record

    def decrypt_database_record(self, encrypted_record: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt PII fields in record"""
        decrypted_record = encrypted_record.copy()

        for field_name in self.pii_fields:
            if field_name in decrypted_record and decrypted_record[field_name]:
                try:
                    decrypted_record[field_name] = self.decrypt_field(
                        decrypted_record[field_name]
                    )
                except ValueError:
                    # Failed to decrypt, leave encrypted
                    pass

        return decrypted_record


class KeyManagement:
    """Cryptographic key lifecycle management"""

    def __init__(self):
        self.keys = {}  # key_id -> {key, version, created, rotated}
        self.current_key_id = None

    def generate_key(self, key_id: str) -> str:
        """Generate new encryption key"""
        key = Fernet.generate_key().decode()

        self.keys[key_id] = {
            'key': key,
            'version': 1,
            'created_at': datetime.utcnow().isoformat(),
            'rotated_at': None,
            'status': 'active'
        }

        if self.current_key_id is None:
            self.current_key_id = key_id

        return key

    def rotate_key(self, key_id: str) -> str:
        """Rotate encryption key (create new version)"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        old_key_data = self.keys[key_id]
        new_key = Fernet.generate_key().decode()

        self.keys[key_id] = {
            'key': new_key,
            'version': old_key_data['version'] + 1,
            'created_at': old_key_data['created_at'],
            'rotated_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'previous_key': old_key_data['key']  # For decryption of old data
        }

        return new_key

    def get_key(self, key_id: str) -> Optional[str]:
        """Get current key"""
        if key_id in self.keys:
            return self.keys[key_id]['key']

        return None


class SecureTransport:
    """TLS/SSL configuration for secure communications"""

    # TLS 1.3 cipher suites (secure, modern)
    SECURE_CIPHERS = (
        'TLS_AES_256_GCM_SHA384:'
        'TLS_CHACHA20_POLY1305_SHA256:'
        'TLS_AES_128_GCM_SHA256'
    )

    @staticmethod
    def create_https_context() -> ssl.SSLContext:
        """Create HTTPS context with TLS 1.3 enforcement"""
        ctx = ssl.create_default_context(cafile=certifi.where())

        # Enforce TLS 1.3 minimum
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3

        # Set secure cipher suites
        ctx.set_ciphers(SecureTransport.SECURE_CIPHERS)

        # Additional hardening
        ctx.options |= ssl.OP_NO_COMPRESSION  # Disable compression (CRIME attack)
        ctx.options |= ssl.OP_CIPHER_SERVER_PREFERENCE  # Server chooses cipher

        return ctx

    @staticmethod
    def create_wss_context() -> ssl.SSLContext:
        """Create WebSocket Secure (WSS) context"""
        return SecureTransport.create_https_context()

    @staticmethod
    def create_mtls_context(
        client_cert: str,
        client_key: str,
        ca_cert: str
    ) -> ssl.SSLContext:
        """Create mutual TLS context for service-to-service auth"""
        ctx = ssl.create_default_context(cafile=ca_cert)

        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED

        # Load client certificate and key
        ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)

        return ctx

    @staticmethod
    def pin_certificate(expected_cert_hash: str, actual_cert: bytes) -> bool:
        """Verify certificate pinning (prevent MITM)"""
        import hashlib

        actual_hash = hashlib.sha256(actual_cert).hexdigest()
        return hashlib.compare_digest(expected_cert_hash, actual_hash)


class SecureHeaders:
    """HTTP security headers for API responses"""

    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
    }

    @staticmethod
    def add_security_headers(response_headers: Dict) -> Dict:
        """Add security headers to response"""
        response_headers.update(SecureHeaders.SECURITY_HEADERS)
        return response_headers
