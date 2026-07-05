from fastapi import APIRouter

from backend.core.config import GROQ_MODEL, groq_api_key_status

router = APIRouter(tags=["Health"])


@router.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Streamlit Chatbot Backend",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "groq_api_key": groq_api_key_status(),
        "model": GROQ_MODEL,
    }
