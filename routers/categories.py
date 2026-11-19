from fastapi import APIRouter, HTTPException, status, Depends
from schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Category


router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    db: Session= Depends(get_db),
) -> Category:
    existing_category = db.scalar(
        select(Category).where(Category.name == category_data.name)
    )

    if existing_category is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists",
        )

    category = Category(**category_data.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create category. Check the name.",
        )
    db.refresh(category)

    return category

@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    categories = db.scalars(select(Category)).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> Category:

    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category ID {category_id} not found",
        )

    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int, 
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
) -> Category:
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category ID {category_id} not found", 
        )

    for key, value in category_data.model_dump().items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"Category ID {category_id} not found",
        )

    db.delete(category)
    db.commit()






    
    