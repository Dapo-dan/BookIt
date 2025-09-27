from pydantic import BaseModel, field_validator

class ServiceCreate(BaseModel):
    title: str
    description: str
    price: float
    duration_minutes: int
    is_active: bool = True

    @field_validator("duration_minutes")
    @classmethod
    def _pos(cls, v):
        if v <= 0: raise ValueError("duration must be positive")
        return v

class ServiceOut(ServiceCreate):
    id: int
