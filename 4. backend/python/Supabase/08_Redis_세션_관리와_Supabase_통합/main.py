"""
실행:
  docker compose up -d
  docker compose exec redis redis-cli ping
  copy .env.example .env
  uvicorn main:app --reload
"""

from fastapi import FastAPI

from config import SUPABASE_URL
from redis_cache.client import r
from routers import auth, conversations, messages, profiles

app = FastAPI(
    title="Supabase + Redis 통합 대화 API",
    description="Auth, 앱 세션, 영구 대화 이력, 최근 대화 캐시를 통합합니다.",
    version="1.0.0",
)

# 기능별로 나뉜 라우터를 앱에 등록합니다.
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(conversations.router)
app.include_router(messages.router)


@app.get("/")
def root():
    return {"message": "Supabase + Redis 통합 대화 API", "docs": "/docs"}


@app.get("/health")
def health():
    # Redis와 Supabase 연결 상태를 함께 확인합니다.
    return {"redis": r.ping(), "supabase_url": SUPABASE_URL}
