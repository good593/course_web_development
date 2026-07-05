"""
환경변수와 앱 설정을 한곳에서 관리합니다.

학생 포인트:
- 비밀값인 API Key는 코드에 직접 쓰지 않고 `.env`에서 읽습니다.
- 라우터나 서비스는 이 파일의 함수/상수를 가져다 쓰기만 합니다.
"""

import os

from dotenv import load_dotenv

# 예제 API Key를 그대로 복사했는지 구분하기 위한 값입니다.
PLACEHOLDER_GROQ_API_KEYS = {
    "gsk_your_api_key_here",
    "your_groq_api_key_here",
}


def reload_env() -> None:
    # override=True로 두면 이미 실행 중인 서버도 `.env`의 최신 값을 다시 읽습니다.
    load_dotenv(override=True)


reload_env()

# FastAPI 앱 정보입니다. Swagger UI 상단에도 표시됩니다.
APP_TITLE = "Streamlit Chatbot Backend"
APP_DESCRIPTION = "Streamlit 화면에서 호출하는 FastAPI + Groq 챗봇 API"
APP_VERSION = "1.0.0"

# 모델명과 시스템 프롬프트는 `.env`에서 바꿀 수 있게 둡니다.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
SYSTEM_PROMPT = os.getenv(
    "CHATBOT_SYSTEM_PROMPT",
    "You are a helpful assistant. You must answer in Korean.",
)


def get_groq_api_key() -> str | None:
    # API Key는 중간에 바꿀 수 있으므로 요청 시점에 다시 읽습니다.
    reload_env()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    return api_key or None


def groq_api_key_status() -> str:
    # /health에서 학생들이 설정 상태를 바로 확인할 수 있도록 문자열로 반환합니다.
    api_key = get_groq_api_key()
    if not api_key:
        return "missing"
    if api_key in PLACEHOLDER_GROQ_API_KEYS:
        return "placeholder"
    return "configured"


def require_groq_api_key() -> str:
    # 실제 Groq 호출 직전에 API Key를 검사합니다.
    # 문제가 있으면 서비스 계층에서 HTTP 오류로 바꿔 클라이언트에 알려줍니다.
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError(".env 파일에 GROQ_API_KEY를 설정해야 합니다.")
    if api_key in PLACEHOLDER_GROQ_API_KEYS:
        raise RuntimeError(
            ".env의 GROQ_API_KEY가 예제값입니다. Groq Console에서 새 API Key를 발급해 넣어주세요."
        )
    return api_key
