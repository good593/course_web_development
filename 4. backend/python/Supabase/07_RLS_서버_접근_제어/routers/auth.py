from fastapi import APIRouter, HTTPException

from database import public_client
from repository import upsert_profile
from schemas import AuthTokenResponse, LoginRequest, SignupRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthTokenResponse)
def signup(data: SignupRequest):
    """Supabase Auth 계정과 서비스용 프로필을 함께 생성합니다."""

    try:
        # Auth 작업은 클라이언트에도 공개할 수 있는 anon key로 수행합니다.
        # display_name은 Auth 사용자의 user_metadata에도 함께 저장합니다.
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
    # auth.users에는 인증 정보가, public.profiles에는 서비스용 정보가 저장됩니다.
    # 두 테이블은 같은 사용자 UUID를 사용하여 1:1로 연결됩니다.
    upsert_profile(user_id, data.email, data.display_name)

    # Confirm email이 꺼져 있으면 세션과 토큰이 즉시 발급됩니다.
    # 켜져 있으면 이메일 확인 전까지 session이 None입니다.
    session = result.session
    return AuthTokenResponse(
        user_id=user_id,
        email=data.email,
        # 세션이 없는 정상 회원가입도 처리할 수 있도록 조건부로 토큰을 읽습니다.
        access_token=session.access_token if session else None,
        refresh_token=session.refresh_token if session else None,
        email_confirm_required=session is None,
    )


@router.post("/login", response_model=AuthTokenResponse)
def login(data: LoginRequest):
    """이메일과 비밀번호를 확인하고 새 인증 세션을 발급합니다."""

    try:
        result = public_client().auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다") from exc

    if not result.user or not result.session:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다")

    # access_token은 API 인증에, refresh_token은 access_token 갱신에 사용합니다.
    return AuthTokenResponse(
        user_id=str(result.user.id),
        email=result.user.email or data.email,
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
    )
