from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.service import ServiceCreate, ServiceOut
from app.models.service import Service
from app.core.dependencies import require_role

router = APIRouter(prefix="/services", tags=["services"])

@router.get("", response_model=list[ServiceOut])
async def list_services(q: str | None = None, price_min: float | None = None, price_max: float | None = None, active: bool | None = None, session: AsyncSession = Depends(get_session)):
    stmt = select(Service)
    if q: stmt = stmt.where(Service.title.ilike(f"%{q}%"))
    if price_min is not None: stmt = stmt.where(Service.price >= price_min)
    if price_max is not None: stmt = stmt.where(Service.price <= price_max)
    if active is not None: stmt = stmt.where(Service.is_active == active)
    res = await session.execute(stmt.order_by(Service.created_at.desc()))
    return res.scalars().all()

@router.get("/{sid}", response_model=ServiceOut)
async def get_service(sid: int, session: AsyncSession = Depends(get_session)):
    s = (await session.execute(select(Service).where(Service.id == sid))).scalar_one_or_none()
    if not s: raise HTTPException(404)
    return s

@router.post("", response_model=ServiceOut, status_code=201, dependencies=[Depends(require_role("admin"))])
async def create_service(data: ServiceCreate, session: AsyncSession = Depends(get_session)):
    s = Service(**data.model_dump())
    session.add(s)
    await session.commit()
    return s

@router.patch("/{sid}", response_model=ServiceOut, dependencies=[Depends(require_role("admin"))])
async def patch_service(sid: int, data: ServiceCreate, session: AsyncSession = Depends(get_session)):
    s = (await session.execute(select(Service).where(Service.id == sid))).scalar_one_or_none()
    if not s: raise HTTPException(404)
    for k, v in data.model_dump().items(): setattr(s, k, v)
    await session.commit()
    return s

@router.delete("/{sid}", status_code=204, dependencies=[Depends(require_role("admin"))])
async def delete_service(sid: int, session: AsyncSession = Depends(get_session)):
    s = (await session.execute(select(Service).where(Service.id == sid))).scalar_one_or_none()
    if not s: raise HTTPException(404)
    await session.delete(s)
    await session.commit()
    return
