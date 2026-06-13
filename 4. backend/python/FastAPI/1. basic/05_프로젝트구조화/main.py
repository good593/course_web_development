from fastapi import FastAPI
from routers.todo import router as todo_router

app = FastAPI(
    title="Todo API",
    description="FastAPI 입문 강의 종합 실습 프로젝트",
    version="1.0.0",
)

app.include_router(todo_router)


@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Todo API에 오신 것을 환영합니다!",
        "docs": "/docs",
        "endpoints": {
            "목록 조회": "GET /todos",
            "단건 조회": "GET /todos/{id}",
            "생성": "POST /todos",
        },
    }
