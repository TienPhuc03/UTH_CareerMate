from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from modules.users.roles import normalize_user_role


UserRole = Literal["candidate", "recruiter", "admin"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = "candidate"

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password cannot be longer than 72 bytes")
        return value

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        return normalize_user_role(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        return normalize_user_role(value)


class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    email: str

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        return normalize_user_role(value)


class TokenData(BaseModel):
    email: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
