from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.booking_repo import BookingRepo
from app.models.booking import Booking, BookingStatus

class BookingService:
    def __init__(self, session: AsyncSession):
        self.repo = BookingRepo(session)
        self.session = session

    async def create(self, *, user_id: int, service_id: int, start: datetime, end: datetime) -> Booking:
        if start >= end:
            raise HTTPException(422, detail="start_time must be before end_time")
        if await self.repo.conflicts(service_id, start, end):
            raise HTTPException(409, detail="Booking overlaps an existing one")
        b = Booking(user_id=user_id, service_id=service_id, start_time=start, end_time=end)
        b = await self.repo.create(b)
        await self.session.commit()
        return b

    async def patch_as_owner(self, *, booking: Booking, start=None, end=None, cancel=False):
        if booking.status not in {BookingStatus.pending, BookingStatus.confirmed}:
            raise HTTPException(409, detail="Cannot modify non-active booking")
        if cancel:
            booking.status = BookingStatus.cancelled
        if start and end:
            if await self.repo.conflicts(booking.service_id, start, end):
                raise HTTPException(409, detail="New time conflicts")
            booking.start_time, booking.end_time = start, end
        await self.session.commit()
        return booking

    async def admin_update_status(self, booking: Booking, status: BookingStatus):
        booking.status = status
        await self.session.commit()
        return booking
