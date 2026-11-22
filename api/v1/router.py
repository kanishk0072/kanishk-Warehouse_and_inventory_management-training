from fastapi import APIRouter

from api.v1 import (
    auth,
    categories,
    products,
    users,
    warehouses,
    inventories,
    # stock_movements,
)


resource_routers = (
    auth.router, products.router, categories.router, warehouses.router, users.router, inventories.router, #stock_movements.router,
)

api_router = APIRouter()
for resource_router in resource_routers:    
    api_router.include_router(resource_router)
