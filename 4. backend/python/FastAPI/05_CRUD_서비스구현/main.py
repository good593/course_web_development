from fastapi import FastAPI

from models.blog import init_db
from routers.posts import router as post_router

init_db()

app = FastAPI(
    title="SQLite Blog API",
    description="FastAPI와 sqlite3 표준 라이브러리로 구현하는 블로그 CRUD API",
    version="1.0.0",
)

app.include_router(post_router)


@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "SQLite Blog API에 오신 것을 환영합니다.",
        "docs": "/docs",
        "database": "blog.db",
        "endpoints": {
            "게시글 목록": "GET /posts",
            "게시글 생성": "POST /posts",
            "게시글 상세": "GET /posts/{post_id}",
            "게시글 수정": "PATCH /posts/{post_id}",
            "게시글 삭제": "DELETE /posts/{post_id}",
        },
    }
