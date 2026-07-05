import os

from dotenv import load_dotenv

PLACEHOLDER_GROQ_API_KEYS = {
    "gsk_your_api_key_here",
    "your_groq_api_key_here",
}


def reload_env() -> None:
    load_dotenv(override=True)


reload_env()

APP_TITLE = "Streamlit Chatbot Backend"
APP_DESCRIPTION = "Streamlit 화면에서 호출하는 FastAPI + Groq 챗봇 API"
APP_VERSION = "1.0.0"

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
SYSTEM_PROMPT = os.getenv(
    "CHATBOT_SYSTEM_PROMPT",
    "You are a helpful assistant. You must answer in Korean.",
)


def get_groq_api_key() -> str | None:
    reload_env()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    return api_key or None


def groq_api_key_status() -> str:
    api_key = get_groq_api_key()
    if not api_key:
        return "missing"
    if api_key in PLACEHOLDER_GROQ_API_KEYS:
        return "placeholder"
    return "configured"


def require_groq_api_key() -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError(".env 파일에 GROQ_API_KEY를 설정해야 합니다.")
    if api_key in PLACEHOLDER_GROQ_API_KEYS:
        raise RuntimeError(
            ".env의 GROQ_API_KEY가 예제값입니다. Groq Console에서 새 API Key를 발급해 넣어주세요."
        )
    return api_key
