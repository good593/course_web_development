from fastapi import FastAPI

from core.config import create_app
from core.openapi import setup_custom_openapi
from routers.health import router as health_router
from routers.orders import router as order_router
from routers.products import router as product_router
from routers.users import router as user_router

app: FastAPI = create_app()

app.include_router(health_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(user_router)

setup_custom_openapi(app)
