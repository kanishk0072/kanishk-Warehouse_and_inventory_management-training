from fastapi import APIRouter

from api.v1 import (
    auth,
    categories,
    products,
    users,
    warehouses,
)


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(categories.router)
api_router.include_router(warehouses.router)
api_router.include_router(users.router)