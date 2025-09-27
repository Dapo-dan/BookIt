from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking, BookingStatus

class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, b: Booking) -> Booking:
        self.session.add(b)
        await self.session.flush()
        return b

    async def by_id(self, bid: int) -> Booking | None:
        res = await self.session.execute(select(Booking).where(Booking.id == bid))
        return res.scalar_one_or_none()

    async def list(self, *, user_id: int | None = None, status: str | None = None, dt_from=None, dt_to=None):
        q = select(Booking)
        if user_id:
            q = q.where(Booking.user_id == user_id)
        if status:
            q = q.where(Booking.status == BookingStatus(status))
        if dt_from:
            q = q.where(Booking.start_time >= dt_from)
        if dt_to:
            q = q.where(Booking.start_time < dt_to)
        res = await self.session.execute(q.order_by(Booking.start_time.desc()))
        return res.scalars().all()

    async def conflicts(self, service_id: int, start, end) -> bool:
        # SQLite-compatible conflict detection
        # Check for overlapping time ranges: (start1 < end2) AND (end1 > start2)
        sql = text("""
        SELECT EXISTS (
          SELECT 1 FROM bookings
          WHERE service_id = :sid
            AND start_time < :end_time
            AND end_time > :start_time
            AND status IN ('pending','confirmed')
        ) AS conflict
        """)
        res = await self.session.execute(sql, {
            "sid": service_id, 
            "start_time": start, 
            "end_time": end
        })
        return bool(res.scalar())
