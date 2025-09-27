from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

class UserPatch(BaseModel):
    name: str | None = None
