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
    # FastAPI 객체는 백엔드 서버의 중심입니다.
    # 제목/설명/버전은 Swagger UI 문서에도 함께 표시됩니다.
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )

    # 기능별 라우터를 연결합니다.
    # main.py에 모든 API를 직접 쓰지 않으면, 학생들이 역할별 파일을 따라가기 쉽습니다.
    app.include_router(health_router)
    app.include_router(chat_router)

    return app


# uvicorn이 `backend.main:app`을 찾을 때 사용하는 실제 FastAPI 앱입니다.
app = create_app()
