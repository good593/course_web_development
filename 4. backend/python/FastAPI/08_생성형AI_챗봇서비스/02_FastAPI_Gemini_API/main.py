"""
20교시 실습: FastAPI + Gemini 연동

main.py는 FastAPI 앱을 만들고 라우터를 등록하는 조립 파일입니다.
실제 요청 처리, Gemini 호출, 세션 관리, 통계 계산은 각 모듈에서 담당합니다.
"""

from fastapi import FastAPI

from core.error_handlers import register_error_handlers
from routers.ask import router as ask_router
from routers.chat import router as chat_router
from routers.stats import router as stats_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Gemini 한국어 챗봇 API",
        description="FastAPI + Gemini 연동 실습",
        version="1.0.0",
    )

    register_error_handlers(app)
    app.include_router(ask_router)
    app.include_router(chat_router)
    app.include_router(stats_router)

    return app


app = create_app()
