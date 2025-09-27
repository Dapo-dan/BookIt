from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: bool = False

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
