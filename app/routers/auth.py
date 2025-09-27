from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.auth import RegisterIn, LoginIn, TokenOut
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token, create_refresh_token, decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
async def register(data: RegisterIn, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(User).where(User.email == data.email))
    if exists.scalar_one_or_none():
        raise HTTPException(409, detail="Email already registered")
    
    role = UserRole.admin if data.is_admin else UserRole.user
    u = User(
        name=data.name, 
        email=data.email, 
        password_hash=hash_password(data.password),
        role=role
    )
    session.add(u)
    await session.commit()
    return {"id": u.id, "email": u.email, "role": u.role.value}

@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(User).where(User.email == payload.email))
    u = res.scalar_one_or_none()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(str(u.id), u.role.value), refresh_token=create_refresh_token(str(u.id)))

bearer = HTTPBearer()

@router.post("/refresh", response_model=TokenOut)
async def refresh(creds: HTTPAuthorizationCredentials = Depends(bearer), session: AsyncSession = Depends(get_session)):
    payload = decode_token(creds.credentials)
    if payload.get("type") != "refresh":
        raise HTTPException(401, detail="Invalid token type")
    user_id = payload.get("sub")
    u = (await session.execute(select(User).where(User.id == int(user_id)))).scalar_one_or_none()
    if not u:
        raise HTTPException(401, detail="User not found")
    return TokenOut(access_token=create_access_token(str(u.id), u.role.value), refresh_token=create_refresh_token(str(u.id)))

@router.post("/logout", status_code=204)
async def logout():
    # With stateless JWT we just return 204. For blacklist, add token store.
    return
