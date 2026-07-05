from groq import Groq

from backend.core.config import require_groq_api_key

_client: Groq | None = None
_client_api_key: str | None = None


def get_client() -> Groq:
    global _client, _client_api_key

    api_key = require_groq_api_key()
    if _client is None or _client_api_key != api_key:
        _client = Groq(api_key=api_key)
        _client_api_key = api_key

    return _client
