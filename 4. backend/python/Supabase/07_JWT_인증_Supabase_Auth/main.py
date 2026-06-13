"""
7교시 실습: JWT 인증과 Supabase Auth 회원가입·로그인

이번 교시 핵심:
  - public_client (anon key) 로 Auth 작업
  - JWT 토큰 발급 및 HTTPBearer로 검증
  - GET /me 로 현재 사용자 확인

실행:
  pip install -r requirements.txt
  copy .env.example .env
  uvicorn main:app --reload
"""

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

security = HTTPBearer()

app = FastAPI(
    title="JWT 인증과 Supabase Auth",
    description="회원가입, 로그인, Bearer 토큰 검증을 실습합니다.",
    version="1.0.0",
)


def public_client() -> Client:
    """anon key — Auth 작업 전용"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    """service_role key — DB 작업 전용"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ── Pydantic 스키마 ─────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class AuthTokenResponse(BaseModel):
    user_id: str
    email: str
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    email_confirm_required: bool = False


class CurrentUser(BaseModel):
    id: str
    email: str


# ── 의존성 ─────────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    token = credentials.credentials
    try:
        result = public_client().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    if not result.user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")

    return CurrentUser(
        id=str(result.user.id),
        email=result.user.email or "",
    )


# ── 엔드포인트 ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "JWT 인증과 Supabase Auth", "docs": "/docs"}


@app.post("/auth/signup", response_model=AuthTokenResponse, tags=["Auth"])
def signup(data: SignupRequest):
    try:
        result = public_client().auth.sign_up({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result.user:
        raise HTTPException(status_code=400, detail="회원가입에 실패했습니다")

    user_id = str(result.user.id)
    session = result.session

    return AuthTokenResponse(
        user_id=user_id,
        email=data.email,
        access_token=session.access_token if session else None,
        refresh_token=session.refresh_token if session else None,
        email_confirm_required=session is None,
    )


@app.post("/auth/login", response_model=AuthTokenResponse, tags=["Auth"])
def login(data: LoginRequest):
    try:
        result = public_client().auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다") from exc

    if not result.user or not result.session:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다")

    return AuthTokenResponse(
        user_id=str(result.user.id),
        email=result.user.email or data.email,
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
    )


@app.get("/me", tags=["Me"])
def get_me(current: CurrentUser = Depends(get_current_user)):
    return {
        "user_id": current.id,
        "email": current.email,
        "message": "인증 성공! 이 정보는 토큰에서 읽었습니다.",
    }
