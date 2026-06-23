from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_session
from redis_cache.client import app_session_key, r
from redis_cache.session import create_app_session
from schemas import AppSession, LoginRequest, LoginResponse, SignupRequest, SignupResponse
from supabase_db.client import public_client
from supabase_db.repository import upsert_profile

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=SignupResponse)
def signup(data: SignupRequest):
    # 1. Supabase Auth에 계정을 생성합니다.
    try:
        result = public_client().auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {"data": {"display_name": data.display_name}},
        })
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result.user:
        raise HTTPException(status_code=400, detail="회원가입에 실패했습니다")

    user_id = str(result.user.id)
    # 2. Supabase DB의 profiles 테이블에 영구 프로필을 저장합니다.
    upsert_profile(user_id, data.email, data.display_name)

    return SignupResponse(
        user_id=user_id,
        email=data.email,
        email_confirm_required=result.session is None,
    )


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    # Supabase Auth가 이메일과 비밀번호를 검증하면 access/refresh token을 발급합니다.
    try:
        result = public_client().auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다") from exc

    if not result.user or not result.session:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다")

    # 발급된 토큰은 Redis 앱 세션에 저장하고 session_id만 응답합니다.
    return create_app_session(
        user_id=str(result.user.id),
        email=result.user.email or data.email,
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
    )


@router.post("/logout")
def logout(session: AppSession = Depends(get_current_session)):
    # Redis에서 앱 세션 키를 삭제하면 이후 같은 session_id 요청은 401이 됩니다.
    deleted = r.delete(app_session_key(session.session_id))
    return {"session_id": session.session_id, "deleted": bool(deleted)}
