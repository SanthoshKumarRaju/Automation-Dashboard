from pydantic import BaseModel, field_validator
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()

    @field_validator('password')
    def password_not_empty(cls, v):
        if not v:
            raise ValueError('Password cannot be empty')
        return v


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    code: Optional[int] = None