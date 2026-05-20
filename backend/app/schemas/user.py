from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


UserRole = Literal["user", "admin"]


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class UserInDB(BaseModel):
    id: str
    username: str
    email: EmailStr
    password_hash: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime