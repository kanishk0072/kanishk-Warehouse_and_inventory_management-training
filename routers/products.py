from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Category, Product
from schemas import ProductCreate, ProductResponse, ProductUpdate, ProductPatch

router = APIRouter(prefix="/products", tags=["Products"])


# @router.get("/", response_model=list[ProductResponse])
# def get_products() -> list[dict]:
#     return products

# def create_product(product: ProductCreate) -> dict:
#     new_product = product.model_dump()
#     products.append(new_product)
#     return new_product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
        product_data: ProductCreate,
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

    return product

@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    products = db.scalars(select(Product)).all()
    return products


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



# @router.get("/{product_id}", response_model=ProductResponse)
# def get_product(product_id: int) -> dict:
#     for product in products:
#         if product["id"] == product_id:
#             return product
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Product ID {product_id} not found"
    # )

# @router.delete("/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
# def delete_product(product_id: int):
#     for product in products:
#         if product["id"] == product_id:
#             products.remove(product)
#             return

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                         detail="product ID {product_id} not found"
#     )
    
# @router.put("/{product_id}",response_model=ProductResponse)
# def update_product(
#     product_id: int,
#     product: ProductUpdate
# ) -> dict:

#     for index, existing_product in enumerate(products):
#         if existing_product["id"] == product_id:

#             updated_product = product.model_dump()
#             updated_product["id"] = product_id

#             products[index] = updated_product
#             return updated_product

#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Product ID {product_id} not found"
#     )

# @router.patch("/{product_id}", response_model=ProductResponse)
# def patch_product(product_id: int, product: ProductPatch) -> dict:
#     for existing_product in products:
#         if existing_product["id"] == product_id:

#             update_data = product.model_dump(exclude_unset=True)

#             if not update_data:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Provide at least one field to update"
#                 )

#             if any(value is None for value in update_data.values()):
#                 raise HTTPException(
#                     status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#                     detail="Fields cannot be null"
#                 )

#             existing_product.update(update_data)
#             return existing_product

#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Product ID {product_id} not found"
#     )