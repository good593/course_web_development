from fastapi import APIRouter, Depends

from dependencies import get_current_session
from redis_cache.client import app_session_key, r
from schemas import AppSession
from supabase_db.client import admin_client
from supabase_db.repository import one_or_404

router = APIRouter(tags=["Profiles"])


@router.get("/me")
def me(session: AppSession = Depends(get_current_session)):
    # Supabase DB에서 현재 사용자의 프로필을 조회합니다.
    result = (
        admin_client()
        .table("profiles")
        .select("*")
        .eq("id", session.user_id)
        .limit(1)
        .execute()
    )
    profile = one_or_404(result.data, "프로필을 찾을 수 없습니다")
    return {
        "profile": profile,
        # Redis에서 현재 세션의 남은 유효 시간을 함께 반환합니다.
        "session_ttl_seconds": r.ttl(app_session_key(session.session_id)),
    }
