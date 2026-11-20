from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Literal

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None

ProductStatus = Literal["active", "discontinued"]


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
