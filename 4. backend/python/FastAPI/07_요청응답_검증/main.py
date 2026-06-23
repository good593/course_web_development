from fastapi import FastAPI

from error_handlers import register_exception_handlers
from routers.orders import router as order_router
from routers.users import router as user_router

app = FastAPI(title="요청·응답 검증 실습")

register_exception_handlers(app)
app.include_router(user_router)
app.include_router(order_router)
