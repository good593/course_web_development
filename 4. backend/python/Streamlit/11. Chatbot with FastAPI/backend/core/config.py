import os

from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "Streamlit Chatbot Backend"
APP_DESCRIPTION = "Streamlit 화면에서 호출하는 FastAPI + Groq 챗봇 API"
APP_VERSION = "1.0.0"

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
SYSTEM_PROMPT = os.getenv(
    "CHATBOT_SYSTEM_PROMPT",
    "You are a helpful assistant. You must answer in Korean.",
)


def get_groq_api_key() -> str | None:
    return os.getenv("GROQ_API_KEY")


def groq_api_key_status() -> str:
    return "configured" if get_groq_api_key() else "missing"


def require_groq_api_key() -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError(".env 파일에 GROQ_API_KEY를 설정해야 합니다.")
    return api_key
