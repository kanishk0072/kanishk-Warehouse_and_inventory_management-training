from fastapi import APIRouter

from api.v1 import (
    auth,
    categories,
    products,
    users,
    warehouses,
)


resource_routers = (
    auth.router, products.router, categories.router, warehouses.router, users.router,
)

api_router = APIRouter()
for resource_router in resource_routers:
    api_router.include_router(resource_router)
