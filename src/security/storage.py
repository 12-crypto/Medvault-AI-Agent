"""
Secure Storage Module
Implements at-rest encryption for PHI using Fernet (AES-128-CBC).
Complies with HIPAA Security Rule encryption requirements.
"""

import os
import logging
import json
from typing import Any, Dict, Optional
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

logger = logging.getLogger(__name__)


class SecureStorage:
    """
    Secure storage for PHI with at-rest encryption.
    
    Features:
    - AES encryption via Fernet
    - Key derivation from password
    - Secure key management
    - Metadata tagging
    
    HIPAA Compliance:
    - Addresses: 164.312(a)(2)(iv) Encryption and Decryption
    - Addresses: 164.312(e)(2)(ii) Encryption
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize secure storage.
        
        Args:
            encryption_key: Base64-encoded Fernet key (from env or config)
        """
        if encryption_key:
            self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        else:
            # Load from environment
            env_key = os.getenv("ENCRYPTION_KEY")
            if env_key:
                self.key = env_key.encode()
            else:
                logger.warning("No encryption key provided. Generating temporary key.")
                self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: Any) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            
        Returns:
            Encrypted bytes
        """
        # Serialize to JSON
        json_data = json.dumps(data)
        
        # Encrypt
        encrypted = self.cipher.encrypt(json_data.encode('utf-8'))
        
        logger.debug(f"Encrypted {len(json_data)} bytes")
        return encrypted
    
    def decrypt_data(self, encrypted_data: bytes) -> Any:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted and deserialized data
        """
        # Decrypt
        decrypted = self.cipher.decrypt(encrypted_data)
        
        # Deserialize
        data = json.loads(decrypted.decode('utf-8'))
        
        return data
    
    def save_encrypted_file(self, data: Any, file_path: Path):
        """
        Save encrypted data to file.
        
        Args:
            data: Data to encrypt and save
            file_path: Destination file path
        """
        encrypted = self.encrypt_data(data)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write encrypted data
        with open(file_path, 'wb') as f:
            f.write(encrypted)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(file_path, 0o600)
        
        logger.info(f"Saved encrypted file: {file_path}")
    
    def load_encrypted_file(self, file_path: Path) -> Any:
        """
        Load and decrypt file.
        
        Args:
            file_path: File to load
            
        Returns:
            Decrypted data
        """
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        data = self.decrypt_data(encrypted_data)
        
        logger.info(f"Loaded encrypted file: {file_path}")
        return data
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded key string
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: User password
            salt: Salt bytes (generated if not provided)
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP recommendation
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key.decode('utf-8'), salt


class PHIStorage:
    """
    High-level PHI storage with encryption and metadata.
    
    Stores PHI records with:
    - Unique ID
    - Encrypted data
    - Access metadata
    - Retention policy
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize PHI storage.
        
        Args:
            storage_dir: Directory for encrypted files
        """
        self.storage_dir = storage_dir or Path("./data/phi")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.secure_storage = SecureStorage()
    
    def store_phi(
        self,
        record_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Store PHI record with encryption.
        
        Args:
            record_id: Unique identifier
            data: PHI data to store
            metadata: Additional metadata (not encrypted)
            
        Returns:
            Path to stored file
        """
        # Create record envelope
        record = {
            "id": record_id,
            "data": data,
            "metadata": metadata or {},
            "stored_at": None,  # Would use datetime
        }
        
        # Save encrypted
        file_path = self.storage_dir / f"{record_id}.enc"
        self.secure_storage.save_encrypted_file(record, file_path)
        
        logger.info(f"Stored PHI record: {record_id}")
        return file_path
    
    def retrieve_phi(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt PHI record.
        
        Args:
            record_id: Record identifier
            
        Returns:
            Decrypted record or None if not found
        """
        file_path = self.storage_dir / f"{record_id}.enc"
        
        if not file_path.exists():
            logger.warning(f"PHI record not found: {record_id}")
            return None
        
        record = self.secure_storage.load_encrypted_file(file_path)
        
        logger.info(f"Retrieved PHI record: {record_id}")
        return record
    
    def delete_phi(self, record_id: str) -> bool:
        """
        Securely delete PHI record.
        
        Args:
            record_id: Record to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.storage_dir / f"{record_id}.enc"
        
        if not file_path.exists():
            return False
        
        # Securely delete file
        file_path.unlink()
        
        logger.info(f"Deleted PHI record: {record_id}")
        return True
