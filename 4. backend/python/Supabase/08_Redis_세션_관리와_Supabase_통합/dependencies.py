from fastapi import Header, HTTPException

from config import SESSION_TTL_SECONDS
from redis_cache.client import app_session_key, r
from redis_cache.session import now_ts
from schemas import AppSession
from supabase_db.client import public_client


def get_current_session(
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
) -> AppSession:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="X-Session-Id 헤더가 필요합니다")

    # 1단계: Redis에 앱 세션이 존재하는지 확인합니다.
    key = app_session_key(x_session_id)
    data = r.hgetall(key)
    if not data:
        raise HTTPException(status_code=401, detail="앱 세션이 없거나 만료되었습니다")

    # 2단계: Redis에 저장된 access_token도 Supabase Auth에서 다시 검증합니다.
    try:
        auth_result = public_client().auth.get_user(data["access_token"])
    except Exception as exc:
        r.delete(key)
        raise HTTPException(status_code=401, detail="Supabase 토큰이 만료되었거나 유효하지 않습니다") from exc

    # 3단계: 토큰 사용자와 Redis 사용자 정보가 같은지 확인합니다.
    if not auth_result.user or str(auth_result.user.id) != data["user_id"]:
        r.delete(key)
        raise HTTPException(status_code=401, detail="세션 사용자 정보가 일치하지 않습니다")

    # 4단계: 정상 요청이 들어오면 마지막 접근 시각과 TTL을 갱신합니다.
    r.hset(key, "last_seen_at", now_ts())
    r.expire(key, SESSION_TTL_SECONDS)

    return AppSession(
        session_id=x_session_id,
        user_id=data["user_id"],
        email=data["email"],
        access_token=data["access_token"],
    )
