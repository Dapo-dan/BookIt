from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Any, Dict
from app.core.config import settings

def _create_token(sub: str, minutes: int, extra: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=minutes)).timestamp()), **extra}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

def create_access_token(user_id: str, role: str) -> str:
    return _create_token(user_id, settings.access_minutes, {"role": role, "type": "access"})

def create_refresh_token(user_id: str) -> str:
    return _create_token(user_id, settings.refresh_minutes, {"type": "refresh"})

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
