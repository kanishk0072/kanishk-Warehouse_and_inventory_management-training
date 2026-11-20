from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


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

