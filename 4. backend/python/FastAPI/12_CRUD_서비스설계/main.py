"""
12교시: CRUD 기반 백엔드 서비스 설계

SQLite를 사용해 실제로 데이터가 저장되는 CRUD API를 만듭니다.
Router / Service / Repository 계층을 분리해 SQL이 라우터로 새지 않게 합니다.

실행: uvicorn main:app --reload
"""
from fastapi import FastAPI

from core.database import init_db
from core.seed import seed_data
from routers.categories import router as category_router
from routers.comments import router as comment_router
from routers.posts import router as post_router


def create_app() -> FastAPI:
    app = FastAPI(title="블로그 API - SQLite CRUD 데모")

    app.include_router(category_router)
    app.include_router(post_router)
    app.include_router(comment_router)

    @app.on_event("startup")
    def startup() -> None:
        init_db()
        seed_data()

    return app


app = create_app()
