import redis

from config import REDIS_URL

# 문자열 기반 JSON 처리와 비교를 위해 Redis 응답을 bytes가 아닌 str로 받습니다.
r = redis.from_url(REDIS_URL, decode_responses=True)


# ── Redis 키 생성 함수 ───────────────────────────────────────────────────
# 키 형식을 한곳에서 관리해 도메인별 키가 섞이지 않게 합니다.

def app_session_key(session_id: str) -> str:
    """앱 세션 데이터를 담는 Redis Hash 키입니다."""
    return f"app_session:{session_id}"


def recent_history_key(user_id: str, conversation_id: str) -> str:
    """사용자별 대화방의 최근 메시지 List 키입니다."""
    return f"recent_history:{user_id}:{conversation_id}"
