import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import Client, create_client

# .env의 값을 현재 프로세스의 환경변수로 불러옵니다.
load_dotenv()

# anon key는 Auth 요청에, service_role key는 서버의 DB 작업에 사용합니다.
# service_role key는 RLS를 우회할 수 있으므로 클라이언트에 절대 노출하면 안 됩니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Authorization: Bearer {token} 헤더에서 Bearer 뒤의 토큰을 추출하는 보안 스키마입니다.
# 이 객체를 Depends()에 사용하면 Swagger UI에도 Authorize 버튼이 생성됩니다.
security = HTTPBearer()

app = FastAPI(
    title="JWT 인증과 Supabase Auth",
    description="회원가입, 로그인, Bearer 토큰 검증을 실습합니다.",
    version="1.0.0",
)


def public_client() -> Client:
    """anon key로 회원가입, 로그인, JWT 사용자 조회를 수행합니다."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    """service_role key로 신뢰할 수 있는 서버 측 DB 작업을 수행합니다."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ── Pydantic 스키마 ─────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    # EmailStr은 이메일 형식을, Field는 문자열 길이를 엔드포인트 실행 전에 검증합니다.
    # 검증에 실패하면 FastAPI가 자동으로 422 응답을 반환합니다.
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    # 현재 예제에서는 입력값만 검증하며 profiles 테이블에는 아직 저장하지 않습니다.
    display_name: str = Field(..., min_length=1, max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class AuthTokenResponse(BaseModel):
    """회원가입과 로그인이 공통으로 사용하는 인증 응답 형식입니다."""

    user_id: str
    email: str
    # 이메일 확인이 필요한 회원가입에서는 세션이 없어 두 토큰이 None일 수 있습니다.
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    email_confirm_required: bool = False


class CurrentUser(BaseModel):
    """검증된 JWT에서 얻은 현재 사용자의 최소 정보입니다."""

    id: str
    email: str


# ── 의존성 ─────────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Bearer 토큰을 Supabase Auth로 검증하고 현재 사용자를 반환합니다."""

    # HTTPBearer가 "Bearer " 접두사를 제거하므로 실제 JWT 문자열만 남습니다.
    # 헤더가 없거나 Bearer 형식이 아니면 이 함수 실행 전에 HTTPBearer가 거부합니다.
    token = credentials.credentials
    try:
        # 서명, 만료 시간 등을 Supabase Auth에 확인하고 토큰 소유자를 가져옵니다.
        result = public_client().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    # SDK 호출은 성공했지만 사용자 정보가 없는 경우도 인증 실패로 처리합니다.
    if not result.user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")

    # 엔드포인트가 Supabase SDK 응답 구조에 직접 의존하지 않도록 변환합니다.
    return CurrentUser(
        id=str(result.user.id),
        email=result.user.email or "",
    )


# ── 엔드포인트 ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    """서버 동작 여부와 Swagger UI 경로를 간단히 안내합니다."""

    return {"message": "JWT 인증과 Supabase Auth", "docs": "/docs"}


@app.post("/auth/signup", response_model=AuthTokenResponse, tags=["Auth"])
def signup(data: SignupRequest):
    """이메일과 비밀번호로 Supabase Auth 사용자를 생성합니다."""

    try:
        # Auth 작업은 브라우저에도 공개 가능한 anon key 클라이언트로 수행합니다.
        result = public_client().auth.sign_up({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result.user:
        raise HTTPException(status_code=400, detail="회원가입에 실패했습니다")

    user_id = str(result.user.id)
    # Confirm email이 꺼져 있으면 즉시 세션과 토큰이 발급됩니다.
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


@app.post("/auth/login", response_model=AuthTokenResponse, tags=["Auth"])
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


@app.get("/me", tags=["Me"])
def get_me(current: CurrentUser = Depends(get_current_user)):
    """유효한 Bearer 토큰을 보낸 현재 사용자의 정보를 반환합니다."""

    # Depends가 먼저 인증을 끝내므로 여기서는 검증된 사용자만 다룹니다.
    return {
        "user_id": current.id,
        "email": current.email,
        "message": "인증 성공! 이 정보는 토큰에서 읽었습니다.",
    }
