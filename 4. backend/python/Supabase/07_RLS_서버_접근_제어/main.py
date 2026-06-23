from fastapi import FastAPI

from routers import auth, conversations, messages, profiles

app = FastAPI(
    title="Supabase Auth 대화 API",
    description="Supabase Auth 토큰으로 현재 사용자를 확인하고 사용자별 데이터를 관리합니다.",
    version="1.0.0",
)

# 기능별로 나뉜 라우터를 앱에 등록합니다.
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(conversations.router)
app.include_router(messages.router)


@app.get("/")
def root():
    """서버 동작 여부와 Swagger UI 경로를 안내합니다."""

    return {"message": "Supabase Auth 대화 API", "docs": "/docs"}
