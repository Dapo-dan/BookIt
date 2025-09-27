from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.session import get_session
from app.core.dependencies import get_current_user, require_role
from app.schemas.booking import BookingCreate, BookingOut, BookingUpdate
from app.services.booking_service import BookingService
from app.models.booking import Booking, BookingStatus

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=BookingOut, status_code=201)
async def create_booking(
    data: BookingCreate, 
    payload=Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    svc = BookingService(session)
    b = await svc.create(
        user_id=int(payload["sub"]), 
        service_id=data.service_id, 
        start=data.start_time, 
        end=data.end_time
    )
    return b

@router.get("", response_model=list[BookingOut])
async def list_bookings(payload=Depends(get_current_user), session: AsyncSession = Depends(get_session), status: str | None = None, from_: datetime | None = None, to: datetime | None = None):
    is_admin = payload.get("role") == "admin"
    from app.repositories.booking_repo import BookingRepo
    repo = BookingRepo(session)
    bookings = await repo.list(user_id=None if is_admin else int(payload["sub"]), status=status, dt_from=from_, dt_to=to)
    return bookings

@router.get("/{bid}", response_model=BookingOut)
async def get_booking(bid: int, payload=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    b = (await session.execute(select(Booking).where(Booking.id == bid))).scalar_one_or_none()
    if not b: raise HTTPException(404)
    if payload.get("role") != "admin" and b.user_id != int(payload["sub"]):
        raise HTTPException(403)
    return b

@router.patch("/{bid}", response_model=BookingOut)
async def patch_booking(
    bid: int, 
    data: BookingUpdate, 
    payload=Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    b = (await session.execute(select(Booking).where(Booking.id == bid))).scalar_one_or_none()
    if not b: 
        raise HTTPException(404, detail="Booking not found")
    
    # Check permissions
    if payload.get("role") != "admin" and b.user_id != int(payload["sub"]):
        raise HTTPException(403, detail="Not your booking")
    
    # Update fields based on role
    if payload.get("role") == "admin":
        # Admin can update status via query parameter
        pass  # Status updates handled separately
    else:
        # Regular users can only reschedule pending/confirmed bookings
        if b.status not in [BookingStatus.pending, BookingStatus.confirmed]:
            raise HTTPException(400, detail="Can only modify pending or confirmed bookings")
        
        if data.start_time is not None:
            b.start_time = data.start_time
        if data.end_time is not None:
            b.end_time = data.end_time
        if data.cancel:
            b.status = BookingStatus.cancelled
    
    await session.commit()
    await session.refresh(b)
    return b

@router.patch("/{bid}/status", response_model=BookingOut, dependencies=[Depends(require_role("admin"))])
async def update_booking_status(
    bid: int,
    status: str,
    payload=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    b = (await session.execute(select(Booking).where(Booking.id == bid))).scalar_one_or_none()
    if not b:
        raise HTTPException(404, detail="Booking not found")
    
    b.status = BookingStatus(status)
    await session.commit()
    await session.refresh(b)
    return b

@router.delete("/{bid}", status_code=204)
async def delete_booking(
    bid: int,
    payload=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    b = (await session.execute(select(Booking).where(Booking.id == bid))).scalar_one_or_none()
    if not b:
        raise HTTPException(404, detail="Booking not found")
    
    # Check permissions
    is_owner = b.user_id == int(payload["sub"])
    is_admin = payload.get("role") == "admin"
    
    if not (is_owner or is_admin):
        raise HTTPException(403, detail="Not authorized")
    
    # Regular users can only delete before start time
    if is_owner and not is_admin:
        from datetime import datetime
        if b.start_time <= datetime.now():
            raise HTTPException(400, detail="Cannot delete booking after start time")
    
    await session.delete(b)
    await session.commit()
    return
