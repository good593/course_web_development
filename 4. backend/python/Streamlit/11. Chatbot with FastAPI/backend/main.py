"""
Streamlit + FastAPI 챗봇 백엔드 진입점.

main.py는 FastAPI 앱을 만들고 라우터를 연결하는 조립 파일입니다.
요청 검증, Groq 호출, 스트리밍 응답은 하위 모듈에서 담당합니다.
"""

from fastapi import FastAPI

from backend.core.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from backend.routers.chat import router as chat_router
from backend.routers.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )

    app.include_router(health_router)
    app.include_router(chat_router)

    return app


app = create_app()
