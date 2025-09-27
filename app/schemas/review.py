from pydantic import BaseModel, field_validator
from datetime import datetime

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def _1to5(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("rating 1–5")
        return v

class ReviewUpdate(BaseModel):
    rating: int | None = None
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def _1to5(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError("rating 1–5")
        return v

class ReviewOut(BaseModel):
    id: int
    booking_id: int
    rating: int
    comment: str | None
    created_at: datetime
