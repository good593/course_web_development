"""
13교시: CRUD 기반 백엔드 서비스 구현

SQLAlchemy + SQLite로 블로그 API를 완성합니다.

실행:
  pip install -r requirements.txt
  uvicorn main:app --reload

Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI

from core.database import Base, engine
from routers.categories import router as category_router
from routers.comments import router as comment_router
from routers.posts import router as post_router

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="블로그 API", version="1.0.0")

app.include_router(category_router)
app.include_router(post_router)
app.include_router(comment_router)
