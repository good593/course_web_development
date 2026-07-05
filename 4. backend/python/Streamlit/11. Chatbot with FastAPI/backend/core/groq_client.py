from groq import Groq

from backend.core.config import require_groq_api_key

_client: Groq | None = None


def get_client() -> Groq:
    global _client

    if _client is None:
        _client = Groq(api_key=require_groq_api_key())

    return _client
