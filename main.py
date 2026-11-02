from fastapi import FastAPI, Depends
from schemas import ProductCreate, ProductResponse
from routers.products import router as products_router, products
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

app = FastAPI(
    title="Warehouse and Inventory Management",
    description="FastAPI Project",
    version="1.0.0",
)
app.include_router(products_router)

@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Warehouse and Inventory Management API"}

@app.get("/db-check", tags=["Database"])
def db_check(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))

    return {
        "status": "success",
        "message": "Database connection is working",
    }

@app.get("/search", response_model=list[ProductResponse])
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