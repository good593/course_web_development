from fastapi import FastAPI
from routers.categories import router as category_router
from routers.products import router as product_router

app = FastAPI(title="Pydantic 데이터 모델링 실습")

app.include_router(category_router)
app.include_router(product_router)
