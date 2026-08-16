"""
Encryptor - Data encryption and decryption
"""

import base64
import hashlib
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class Encryptor:
    """
    Encryptor for data encryption and decryption using Fernet symmetric encryption.
    """
    
    def __init__(self, secret_key: str):
        """
        Initialize the encryptor.
        
        Args:
            secret_key: Secret key for encryption
        """
        self.secret_key = secret_key
        self._fernet = self._create_fernet() if CRYPTO_AVAILABLE else None
    
    def _create_fernet(self) -> Fernet:
        """
        Create a Fernet instance from the secret key.
        
        Returns:
            Fernet instance
        """
        # Derive a proper encryption key from the secret key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'salt_',  # In production, use a random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt data.
        
        Args:
            data: Plain text data
            
        Returns:
            Encrypted data (base64 encoded)
        """
        if not CRYPTO_AVAILABLE or not self._fernet:
            raise ValueError("Encryption not available - cryptography library not installed")
        
        try:
            encrypted = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data (base64 encoded)
            
        Returns:
            Decrypted plain text
        """
        if not CRYPTO_AVAILABLE or not self._fernet:
            raise ValueError("Decryption not available - cryptography library not installed")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """
        Encrypt binary data.
        
        Args:
            data: Binary data
            
        Returns:
            Encrypted binary data
        """
        if not CRYPTO_AVAILABLE or not self._fernet:
            raise ValueError("Encryption not available - cryptography library not installed")
        
        try:
            return self._fernet.encrypt(data)
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt binary data.
        
        Args:
            encrypted_data: Encrypted binary data
            
        Returns:
            Decrypted binary data
        """
        if not CRYPTO_AVAILABLE or not self._fernet:
            raise ValueError("Decryption not available - cryptography library not installed")
        
        try:
            return self._fernet.decrypt(encrypted_data)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def hash_data(self, data: str) -> str:
        """
        Hash data using SHA-256.
        
        Args:
            data: Data to hash
            
        Returns:
            Hashed data (hex string)
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """
        Verify data against a hash.
        
        Args:
            data: Original data
            hash_value: Hash to verify against
            
        Returns:
            True if hash matches, False otherwise
        """
        return self.hash_data(data) == hash_value
    
    def generate_key(self) -> str:
        """
        Generate a new encryption key.
        
        Returns:
            Base64 encoded encryption key
        """
        if not CRYPTO_AVAILABLE:
            raise ValueError("Key generation not available - cryptography library not installed")
        
        return Fernet.generate_key().decode()
    
    def is_available(self) -> bool:
        """
        Check if encryption is available.
        
        Returns:
            True if encryption is available
        """
        try:
            test_data = "test"
            encrypted = self.encrypt(test_data)
            decrypted = self.decrypt(encrypted)
            return test_data == decrypted
        except:
            return False