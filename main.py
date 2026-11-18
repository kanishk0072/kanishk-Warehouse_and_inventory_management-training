from fastapi import FastAPI, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from database import get_db, settings
from api.v1.router import api_router
import logging
import time

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


app = FastAPI(
    title="Warehouse and Inventory Management",
    description="FastAPI Project",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Client-Source",
    ],
    expose_headers=["X-Process-Time-Ms"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s | Status: %s | Time: %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    response.headers["X-Process-Time-Ms"] = f"{duration:.2f}"

    return response