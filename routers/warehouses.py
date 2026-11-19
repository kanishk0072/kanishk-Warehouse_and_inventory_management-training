from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User, Warehouse
from schemas import (
    WarehouseCreate,
    WarehousePatch,
    WarehouseResponse,
    WarehouseUpdate,
)

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post(
    "",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
):
    warehouse = Warehouse(**warehouse_data.model_dump())
    db.add(warehouse)

    try:
        db.commit()
        db.refresh(warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create warehouse",
        )

    return warehouse


@router.get("", response_model=list[WarehouseResponse])
def list_warehouses(db: Session = Depends(get_db)) -> list[Warehouse]:
    warehouses = db.scalars(select(Warehouse)).all()
    return warehouses


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        )

    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        )

    for field, value in warehouse_data.model_dump().items():
        setattr(warehouse, field, value)

    try:
        db.commit()
        db.refresh(warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update warehouse",
        )

    return warehouse


@router.patch("/{warehouse_id}", response_model=WarehouseResponse)
def patch_warehouse(
    warehouse_id: int,
    warehouse_data: WarehousePatch,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        )

    changes = warehouse_data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update",
        )

    for field, value in changes.items():
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null",
            )

        setattr(warehouse, field, value)

    try:
        db.commit()
        db.refresh(warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update warehouse",
        )

    return warehouse


@router.delete(
    "/{warehouse_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        )

    assigned_user = db.scalar(
        select(User.id)
        .where(User.warehouse_id == warehouse_id)
        .limit(1)
    )

    if assigned_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse cannot be deleted while users are assigned to it",
        )

    db.delete(warehouse)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse is referenced by other records and cannot be deleted",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
