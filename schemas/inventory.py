from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StockMovementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: int = Field(gt=0)
    movement_type: Literal["IN", "OUT"]
    quantity: int = Field(gt=0)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    product_id: int
    quantity: int


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_id: int
    movement_type: str
    quantity: int
    created_at: datetime