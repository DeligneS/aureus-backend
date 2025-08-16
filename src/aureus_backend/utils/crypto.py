"""Encryption utilities for secure token storage."""
import os
from typing import Optional
from cryptography.fernet import Fernet

def get_fernet() -> Fernet:
    """Get the Fernet instance using the master key from environment."""
    master_key = os.environ.get("AUREUS_MASTER_KEY")
    if not master_key:
        raise RuntimeError("AUREUS_MASTER_KEY environment variable not set")
    return Fernet(master_key.encode())

# Initialize Fernet instance
FERNET = get_fernet()

def encrypt(value: Optional[str]) -> Optional[str]:
    """Encrypt a string value using Fernet symmetric encryption."""
    if value is None:
        return None
    return FERNET.encrypt(value.encode()).decode()

def decrypt(value: Optional[str]) -> Optional[str]:
    """Decrypt a Fernet-encrypted string."""
    if value is None:
        return None
    return FERNET.decrypt(value.encode()).decode()

# Convenience aliases
enc = encrypt
dec = decrypt
