from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from redis_client import redis_client

from auth_dependencies import get_current_user
from database import get_db
from models import User, Warehouse, Product, Inventory, StockMovement
from schemas.inventory import (
    StockMovementCreate,
    InventoryResponse,
    StockMovementResponse,
)


router = APIRouter(
    prefix="/warehouses/{warehouse_id}",
    tags=["Inventory"],
)


def check_warehouse_access(
    warehouse_id: int,
    db: Session,
    user: User,
):
    if user.role != "admin" and user.warehouse_id != warehouse_id:
        raise HTTPException(403, "Warehouse access denied")

    if db.get(Warehouse, warehouse_id) is None:
        raise HTTPException(404, "Warehouse not found")


# 1. VIEW INVENTORY
@router.get(
    "/inventory",
    response_model=list[InventoryResponse],
    summary="View warehouse inventory",
)
def list_inventory(
    warehouse_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_warehouse_access(warehouse_id, db, user)

    return db.scalars(
        select(Inventory)
        .where(Inventory.warehouse_id == warehouse_id)
        .order_by(Inventory.id)
        .offset(skip)
        .limit(limit)
    ).all()


# 2. STOCK IN / OUT
@router.post(
    "/stock-movements",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add or remove stock",
)
def create_stock_movement(
    warehouse_id: int,
    data: StockMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_warehouse_access(warehouse_id, db, user)

    if db.get(Product, data.product_id) is None:
        raise HTTPException(404, "Product not found")

    inventory = db.scalar(
        select(Inventory)
        .where(
            Inventory.warehouse_id == warehouse_id,
            Inventory.product_id == data.product_id,
        )
        .with_for_update()
    )

    if inventory is None and data.movement_type == "OUT":
        raise HTTPException(409, "Insufficient stock")

    try:
        if inventory is None:
            inventory = Inventory(
                warehouse_id=warehouse_id,
                product_id=data.product_id,
                quantity=0,
            )
            db.add(inventory)
            db.flush()

        if data.movement_type == "IN":
            inventory.quantity += data.quantity
        else:
            if inventory.quantity < data.quantity:
                raise HTTPException(409, "Insufficient stock")

            inventory.quantity -= data.quantity

        movement = StockMovement(
            inventory_id=inventory.id,
            movement_type=data.movement_type,
            quantity=data.quantity,
        )

        db.add(movement)
        db.commit()
        redis_client.delete(
            f"dashboard:warehouse:{warehouse_id}:v1"
        )
        db.refresh(movement)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            "Concurrent stock update; please retry",
        )

    return movement


# 3. STOCK MOVEMENT HISTORY
@router.get(
    "/stock-movements",
    response_model=list[StockMovementResponse],
    summary="View stock movement history",
)
def list_stock_movements(
    warehouse_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_warehouse_access(warehouse_id, db, user)

    return db.scalars(
        select(StockMovement)
        .join(Inventory)
        .where(Inventory.warehouse_id == warehouse_id)
        .order_by(StockMovement.id.desc())
        .offset(skip)
        .limit(limit)
    ).all()