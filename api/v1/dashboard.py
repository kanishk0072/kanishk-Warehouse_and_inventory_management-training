import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from auth_dependencies import get_current_user
from database import get_db
from models import User, Warehouse, WarehouseMember, Inventory
from redis_client import redis_client

router = APIRouter(prefix="/warehouses", tags=["Dashboard"])


@router.get("/{warehouse_id}/dashboard")
def get_dashboard(
    warehouse_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if warehouse is None:
        raise HTTPException(404, "Warehouse not found")

    membership = db.scalar(
        select(WarehouseMember.id).where(
            WarehouseMember.warehouse_id == warehouse_id,
            WarehouseMember.user_id == user.id,
        )
    )

    allowed = (
        user.role == "admin"
        or warehouse.owner_id == user.id
        or membership is not None
        or user.warehouse_id == warehouse_id
    )

    if not allowed:
        raise HTTPException(403, "Warehouse access denied")

    cache_key = f"dashboard:warehouse:{warehouse_id}:v1"
    cached = redis_client.get(cache_key)

    if cached is not None:
        return json.loads(cached)

    product_count, total_units = db.execute(
        select(
            func.count(Inventory.id),
            func.coalesce(func.sum(Inventory.quantity), 0),
        ).where(Inventory.warehouse_id == warehouse_id)
    ).one()

    low_stock_count = db.scalar(
        select(func.count(Inventory.id)).where(
            Inventory.warehouse_id == warehouse_id,
            Inventory.quantity <= 5,
        )
    ) or 0

    result = {
        "warehouse_id": warehouse_id,
        "product_count": product_count,
        "total_units": int(total_units),
        "low_stock_count": low_stock_count,
    }

    redis_client.set(cache_key, json.dumps(result), ex=60)
    return result
