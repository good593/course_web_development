import time
from uuid import uuid4

from config import SESSION_TTL_SECONDS
from redis_cache.client import app_session_key, r
from schemas import LoginResponse


def now_ts() -> int:
    return int(time.time())


def create_app_session(user_id: str, email: str, access_token: str, refresh_token: str) -> LoginResponse:
    # 클라이언트에는 Supabase 토큰 대신 임의의 앱 session_id만 전달합니다.
    session_id = str(uuid4())
    key = app_session_key(session_id)
    # 토큰과 사용자 정보는 서버 측 Redis Hash에만 보관합니다.
    r.hset(
        key,
        mapping={
            "user_id": user_id,
            "email": email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": now_ts(),
            "last_seen_at": now_ts(),
        },
    )
    # 세션 키 전체에 TTL을 설정해 오래된 세션을 Redis가 자동 정리하게 합니다.
    r.expire(key, SESSION_TTL_SECONDS)
    return LoginResponse(
        session_id=session_id,
        user_id=user_id,
        email=email,
        ttl_seconds=r.ttl(key),
    )
