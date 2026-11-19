from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=10)
    description: str | None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)