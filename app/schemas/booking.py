from pydantic import BaseModel
from datetime import datetime

class BookingCreate(BaseModel):
    service_id: int
    start_time: datetime
    end_time: datetime

class BookingUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    cancel: bool = False

class BookingOut(BaseModel):
    id: int
    user_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
