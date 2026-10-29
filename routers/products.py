from fastapi import APIRouter, HTTPException, status
from schemas import ProductCreate, ProductResponse, ProductUpdate, ProductPatch

router = APIRouter()

products: list[dict] = []

@router.get("/products", response_model=list[ProductResponse])
def get_products() -> list[dict]:
    return products

@router.post("/products", response_model=ProductResponse,status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate) -> dict:
    new_product = product.model_dump()
    products.append(new_product)
    return new_product

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int) -> dict:
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product ID {product_id} not found"
    )

@router.delete("/products/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="product ID {product_id} not found"
    )
    
@router.put("/products/{product_id}",response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate
) -> dict:

    for index, existing_product in enumerate(products):
        if existing_product["id"] == product_id:

            updated_product = product.model_dump()
            updated_product["id"] = product_id

            products[index] = updated_product
            return updated_product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product ID {product_id} not found"
    )

@router.patch("/products/{product_id}", response_model=ProductResponse)
def patch_product(product_id: int, product: ProductPatch) -> dict:
    for existing_product in products:
        if existing_product["id"] == product_id:

            update_data = product.model_dump(exclude_unset=True)

            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide at least one field to update"
                )

            if any(value is None for value in update_data.values()):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Fields cannot be null"
                )

            existing_product.update(update_data)
            return existing_product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product ID {product_id} not found"
    )