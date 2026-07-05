"""
서버 상태를 확인하는 간단한 API 라우터입니다.
"""

from fastapi import APIRouter

from backend.core.config import GROQ_MODEL, groq_api_key_status

# tags 값은 Swagger UI에서 API 그룹 이름으로 보입니다.
router = APIRouter(tags=["Health"])


@router.get("/")
def read_root() -> dict[str, str]:
    # 브라우저에서 서버 주소만 열었을 때 안내용으로 보여 주는 기본 응답입니다.
    return {
        "message": "Streamlit Chatbot Backend",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    # 실제 Groq 호출 전에도 서버와 환경변수 상태를 빠르게 확인할 수 있습니다.
    return {
        "status": "ok",
        "groq_api_key": groq_api_key_status(),
        "model": GROQ_MODEL,
    }
