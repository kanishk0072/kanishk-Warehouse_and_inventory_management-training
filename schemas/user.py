from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Literal

UserRole = Literal["admin", "manager", "staff"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr 
    role: UserRole | None = "staff"
    password: str = Field(min_length=8, max_length=128)
    warehouse_id: int | None = Field(default=None, gt=0)


class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    role: UserRole
    warehouse_id: int | None


class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    role: UserRole | None = None
    warehouse_id: int | None = Field(default=None, gt=0)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    warehouse_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


