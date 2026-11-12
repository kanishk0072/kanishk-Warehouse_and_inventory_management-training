from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from typing import Literal

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None

ProductStatus = Literal["active", "discontinued"]
UserRole = Literal["admin", "manager", "staff"]


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    sku: str = Field(min_length=1, max_length=50)
    description: str | None = None
    unit_price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    status: ProductStatus = "active"
    category_id: int | None = None


class ProductUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    sku: str = Field(min_length=1, max_length=50)
    description: str | None
    unit_price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    status: ProductStatus
    category_id: int | None

class CategoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=10)
    description: str | None


class ProductPatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    description: str | None = None
    unit_price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    status: ProductStatus | None = None
    category_id: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: str | None
    unit_price: Decimal
    status: ProductStatus
    category_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=255)


class WarehouseUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=255)


class WarehousePatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    location: str | None = Field(default=None, min_length=2, max_length=255)


class WarehouseResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

