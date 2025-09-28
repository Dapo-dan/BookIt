from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: bool = False
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Password cannot be empty')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (maximum 72 bytes)')
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class LoginIn(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Password cannot be empty')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (maximum 72 bytes)')
        return v

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
