
from fastapi import FastAPI
from schemas import ProductCreate, ProductResponse

app = FastAPI(
    title="Warehouse Inventory Management API",
    description="Module 1: FastAPI introduction and Python fundamentals",
    version="1.0.0",
)

products: list[dict] = []

@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Warehouse and Inventory Management API"}

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate) -> dict:
    new_product = product.model_dump()
    products.append(new_product)
    return new_product

@app.get("/products", response_model=list[ProductResponse])
def get_products() -> list[dict]:
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int) -> dict:
    for product in products:
        if product["id"] == product_id:
            return product

    return {"message": f"Product {product_id} not found"}


@app.get("/search", response_model=ProductResponse)
def search_products(
    q: str = "",
    category: str | None = None,
) -> list[dict]:
    results = products

    if q:
        results = [
            product
            for product in results
            if q.lower() in product["name"].lower()
        ]

    if category:
        results = [
        product for product in results
        if product["category"]["name"].lower() == category.lower()
    ]

    return results