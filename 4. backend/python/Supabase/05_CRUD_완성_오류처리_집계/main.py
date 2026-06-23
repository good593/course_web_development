from fastapi import FastAPI

from routers import conversations, messages, users

app = FastAPI(
    title="FastAPI + Supabase 서비스 API",
    description="Supabase를 데이터 저장소로 사용하는 사용자별 대화 API",
    version="1.0.0",
)

# 기능별로 나뉜 라우터를 앱에 등록한다.
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(messages.router)


@app.get("/")
def root():
    return {"message": "FastAPI + Supabase 서비스 API", "docs": "/docs"}
