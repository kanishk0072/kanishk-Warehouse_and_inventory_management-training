from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Response, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from auth_dependencies import get_current_user, require_admin

from database import get_db
from models import Category, Product, User
from schemas import ProductCreate, ProductResponse, ProductUpdate, ProductPatch
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
    category_id: int | None = None,
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = None,
):
    skip = pagination["skip"]
    limit = pagination["limit"]

    query = select(Product)

    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    if status_filter:
        query = query.where(Product.status == status_filter)

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0

    cache_key = (
        f"products:list:v1:skip={skip}:limit={limit}"
        f":category={category_id}:status={status_filter}:search={search}"
    )

    cached = redis_client.get(cache_key)

    if cached is not None:
        items = json.loads(cached)
        response.headers["X-Cache"] = "HIT"
    else:
        products = db.scalars(
            query.order_by(Product.id)
            .offset(skip)
            .limit(limit)
        ).all()

        items = [
            ProductResponse.model_validate(
                product, from_attributes=True
            ).model_dump(mode="json")
            for product in products
        ]

        redis_client.set(cache_key, json.dumps(items), ex=60)
        response.headers["X-Cache"] = "MISS"

    return {
        "success": True,
        "data": {
            "total": total,
            "page": skip // limit + 1,
            "limit": limit,
            "items": items,
        },
    }

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

@router.patch("/{product_id}", response_model=ProductResponse)
def patch_product(
    product_id: int,
    product_data: ProductPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(404, "Product not found")

    changes = product_data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(400, "Provide at least one field")

    allowed_fields = {
        "name", "description", "unit_price",
        "status", "category_id",
    }

    if set(changes) - allowed_fields:
        raise HTTPException(422, "Unsupported fields")

    for field in ("name", "unit_price", "status"):
        if field in changes and changes[field] is None:
            raise HTTPException(422, f"{field} cannot be null")

    if "category_id" in changes:
        category_id = changes["category_id"]
        if category_id is not None and db.get(Category, category_id) is None:
            raise HTTPException(404, "Category not found")

    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Could not update product")

    invalidate_products_cache()

    return product
