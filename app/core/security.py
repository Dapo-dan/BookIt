from passlib.context import CryptContext
from app.core.config import settings
import logging

# Configure bcrypt with specific parameters to avoid version detection issues
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__min_rounds=10,
    bcrypt__max_rounds=15
)

logger = logging.getLogger(__name__)

def _truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes to comply with bcrypt limitations.
    Handles UTF-8 encoding properly by truncating at character boundaries.
    """
    if not password:
        return password
    
    # Convert to bytes to check length
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) <= 72:
        return password
    
    # Truncate to 72 bytes, but ensure we don't break UTF-8 characters
    truncated_bytes = password_bytes[:72]
    
    # Find the last complete UTF-8 character
    while truncated_bytes and truncated_bytes[-1] & 0x80 and not (truncated_bytes[-1] & 0x40):
        truncated_bytes = truncated_bytes[:-1]
    
    return truncated_bytes.decode('utf-8', errors='ignore')

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with proper length handling.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Truncate password to comply with bcrypt's 72-byte limit
    truncated_password = _truncate_password(password)
    
    try:
        return pwd_context.hash(truncated_password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise ValueError("Failed to hash password")

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash using bcrypt.
    """
    if not password or not hashed:
        return False
    
    # Apply the same truncation logic as in hash_password
    truncated_password = _truncate_password(password)
    
    try:
        return pwd_context.verify(truncated_password, hashed)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False
