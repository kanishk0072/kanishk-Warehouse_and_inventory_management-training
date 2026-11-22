from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from auth_dependencies import get_current_user

from database import get_db
from models import Category, Product
from schemas import ProductCreate, ProductResponse, ProductUpdate, ProductPatch, product
from dependencies.pagination import get_pagination
from tasks.inventory_notification import notify_inventory_team
from tasks.welcome_email import simulate_welcome_email
from redis_client import redis_client   
import json

router = APIRouter(prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)],)


def invalidate_products_cache():
    for key in redis_client.scan_iter(
        match="products:list:v1:*"
    ):
        redis_client.delete(key)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
        product_data: ProductCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
) -> Product:
    existing_product = db.scalar(
        select(Product).where(Product.sku == product_data.sku)
    )

    if existing_product is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with this SKU already exists",
        )

    if product_data.category_id is not None:
        category = db.get(Category, product_data.category_id)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    product = Product(**product_data.model_dump())
    db.add(product)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="could not create product check sku and category",
        )
    db.refresh(product)

    invalidate_products_cache()
    notify_inventory_team.delay(product.sku)

    return product

@router.get(
    "/",
    response_model=dict,
    summary="List products",
    description="Fetch products with pagination.",
)
def list_products(
    response: Response,
    db: Session = Depends(get_db),
    pagination: dict[str, int] = Depends(get_pagination),
):
    skip = pagination["skip"]
    limit = pagination["limit"]

    total = db.scalar(select(func.count()).select_from(Product)) or 0

    def format_response(items):
        return {
            "success": True,
            "data": {
                "total": total,
                "page": skip // limit + 1,
                "limit": limit,
                "items": items,
            },
        }
        

    cache_key = f"products:list:v1:skip={skip}:limit={limit}"

    # Check Redis cache
    cached_products = redis_client.get(cache_key)

    if cached_products is not None:
        response.headers["X-Cache"] = "HIT"
        return format_response(json.loads(cached_products))

    # Fetch from PostgreSQL on cache miss
    products = db.scalars(
        select(Product)
        .order_by(Product.id)
        .offset(skip)
        .limit(limit)
    ).all()

    # Convert ORM objects to JSON-compatible data
    product_data = [
        ProductResponse.model_validate(
            product,
            from_attributes=True,
        ).model_dump(mode="json")
        for product in products
    ]

    # Save in Redis for 60 seconds
    redis_client.set(
        cache_key,
        json.dumps(product_data),
        ex=60,
    )

    response.headers["X-Cache"] = "MISS"

    return format_response(product_data)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ID {product_id} not found",
        )

    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ID {product_id} not found",
        )

    for key, value in product_data.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    invalidate_products_cache()

    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ID {product_id} not found",
        )

    db.delete(product)
    db.commit()
    invalidate_products_cache()
