"""
Groq SDK 클라이언트를 생성하고 재사용하는 파일입니다.

학생 포인트:
요청이 올 때마다 SDK 객체를 새로 만들지 않고, 한 번 만든 객체를 캐시에 저장해 둡니다.
"""

from groq import Groq

from backend.core.config import require_groq_api_key

# Groq 클라이언트와 그때 사용한 API Key를 함께 기억합니다.
_client: Groq | None = None
_client_api_key: str | None = None


def get_client() -> Groq:
    global _client, _client_api_key

    api_key = require_groq_api_key()
    # `.env`의 API Key가 바뀌면 이전 클라이언트를 버리고 새 클라이언트를 만듭니다.
    if _client is None or _client_api_key != api_key:
        _client = Groq(api_key=api_key)
        _client_api_key = api_key

    return _client
