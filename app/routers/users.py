from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.core.dependencies import get_current_user
from app.schemas.user import UserOut, UserPatch
from app.models.user import User

router = APIRouter(prefix="/me", tags=["users"])

@router.get("", response_model=UserOut)
async def me(payload=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    u = (await session.execute(select(User).where(User.id == int(payload["sub"])))).scalar_one()
    return UserOut(id=u.id, name=u.name, email=u.email, role=u.role.value)

@router.patch("", response_model=UserOut)
async def patch_me(data: UserPatch, payload=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    u = (await session.execute(select(User).where(User.id == int(payload["sub"])))).scalar_one()
    if data.name: u.name = data.name
    await session.commit()
    return UserOut(id=u.id, name=u.name, email=u.email, role=u.role.value)
