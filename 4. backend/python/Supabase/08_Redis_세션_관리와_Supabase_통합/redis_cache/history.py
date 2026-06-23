import json

from config import RECENT_HISTORY_LIMIT, RECENT_HISTORY_TTL_SECONDS
from redis_cache.client import r, recent_history_key


def append_recent_message(user_id: str, conversation_id: str, message: dict) -> None:
    key = recent_history_key(user_id, conversation_id)
    # 오래된 메시지부터 읽을 수 있도록 List 오른쪽에 JSON 문자열을 추가합니다.
    r.rpush(key, json.dumps(message, ensure_ascii=False))
    # LTRIM으로 최근 N개만 남기고, 캐시 자체에도 별도 TTL을 적용합니다.
    r.ltrim(key, -RECENT_HISTORY_LIMIT, -1)
    r.expire(key, RECENT_HISTORY_TTL_SECONDS)
