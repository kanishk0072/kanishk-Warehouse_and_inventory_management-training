from fastapi import FastAPI
from schemas import ProductCreate, ProductResponse
from routers.products import router as products_router, products

app = FastAPI(
    title="Warehouse and Inventory Management",
    description="FastAPI Project",
    version="1.0.0",
)
app.include_router(products_router)

@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Warehouse and Inventory Management API"}

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