from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User, Warehouse
from schemas import (
    UserCreate,
    UserPatch,
    UserResponse,
    UserRole,
    UserUpdate,
)
from security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


def check_warehouse(db: Session, warehouse_id: int | None) -> None:
    if warehouse_id is not None and db.get(Warehouse, warehouse_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        )


def validate_role_assignment(
    role: UserRole,
    warehouse_id: int | None,
) -> None:
    if role == "manager" and warehouse_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A manager must be assigned to a warehouse",
        )

    if role == "admin" and warehouse_id is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A global admin must not be assigned to a single warehouse",
        )


def check_email(
    db: Session,
    email: str,
    exclude_user_id: int | None = None,
) -> None:
    statement = select(User.id).where(
        func.lower(User.email) == email.lower()
    )

    if exclude_user_id is not None:
        statement = statement.where(User.id != exclude_user_id)

    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    email = str(user_data.email).lower()

    check_email(db, email)
    check_warehouse(db, user_data.warehouse_id)
    validate_role_assignment(user_data.role, user_data.warehouse_id)

    user = User(
        name=user_data.name,
        email=email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        warehouse_id=user_data.warehouse_id,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create user; check email and warehouse",
        )

    return user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    users = db.scalars(select(User)).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    email = str(user_data.email).lower()

    check_email(db, email, exclude_user_id=user_id)
    check_warehouse(db, user_data.warehouse_id)
    validate_role_assignment(user_data.role, user_data.warehouse_id)

    user.name = user_data.name
    user.email = email
    user.role = user_data.role
    user.warehouse_id = user_data.warehouse_id

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update user; check email and warehouse",
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user(
    user_id: int,
    user_data: UserPatch,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    changes = user_data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update",
        )

    for field in ("name", "email", "role"):
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null",
            )

    if "email" in changes:
        changes["email"] = str(changes["email"]).lower()
        check_email(
            db,
            changes["email"],
            exclude_user_id=user_id,
        )

    new_role = changes.get("role", user.role)
    new_warehouse_id = changes.get("warehouse_id", user.warehouse_id)

    check_warehouse(db, new_warehouse_id)
    validate_role_assignment(new_role, new_warehouse_id)

    for field, value in changes.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update user; check email and warehouse",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted because other records reference this user",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
