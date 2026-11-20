from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from redis_client import redis_client

from database import get_db, settings
from api.v1.router import api_router
import logging
import time
import uuid

from logging_config import configure_logging, request_id_ctx


configure_logging()
logger = logging.getLogger("warehouse.api")

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
    expose_headers=["X-Process-Time-Ms", "X-Request-ID"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    token = request_id_ctx.set(request_id)

    start = time.perf_counter()

    try:
        response = await call_next(request)

        duration = round(
            (time.perf_counter() - start) * 1000, 2
        )

        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration,
            },
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration)

        return response

    except Exception:
        logger.exception("request_failed")
        raise

    finally:
        request_id_ctx.reset(token)

@app.get("/health", tags=["Health"])
def health_check():
    logger.info("health_check_called")
    return {"status": "healthy"}

@app.get("/ready", tags=["Health"])
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        redis_client.ping()

        return {
            "status": "ready",
            "postgres": "connected",
            "redis": "connected",
        }

    except (SQLAlchemyError, RedisError):
        logger.exception("readiness_check_failed")

        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable",
        )
