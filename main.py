
from fastapi import FastAPI

app = FastAPI(
    title="Warehouse Inventory Management API",
    description="Module 1: FastAPI introduction and Python fundamentals",
    version="1.0.0",
)

# Hardcoded sample data for Module 1
products = [
    {
        "id": 101,
        "name": "Wireless Mouse",
        "category": "Electronics",
        "quantity": 50,
    },
    {
        "id": 102,
        "name": "Mechanical Keyboard",
        "category": "Electronics",
        "quantity": 25,
    },
    {
        "id": 103,
        "name": "Office Chair",
        "category": "Furniture",
        "quantity": 12,
    },
]


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Warehouse and Inventory Management API"}


@app.get("/products")
def get_products() -> list[dict]:
    return products


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    for product in products:
        if product["id"] == product_id:
            return product

    return {"message": f"Product {product_id} not found"}


@app.get("/search")
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
            product
            for product in results
            if product["category"].lower() == category.lower()
        ]

    return results