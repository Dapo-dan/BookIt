from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # bcrypt has a 72-byte limit for passwords
    # Truncate password if it's longer than 72 bytes
    if len(p.encode('utf-8')) > 72:
        p = p[:72]
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    # Apply the same truncation logic as in hash_password
    if len(p.encode('utf-8')) > 72:
        p = p[:72]
    return pwd_context.verify(p, hashed)
