from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth import decode_token

bearer = HTTPBearer(auto_error=False)

async def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(creds.credentials)
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        return payload  # contains sub=user_id, role
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_role(role: str):
    async def _inner(payload: dict = Depends(get_current_user)):
        if payload.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return payload
    return _inner
