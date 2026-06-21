"""
3교시 실습: Supabase Auth 기반 회원가입/로그인과 사용자별 접근 제어

실행:
  pip install -r requirements.txt
  copy .env.example .env
  uvicorn main:app --reload
"""

import os
from typing import Literal

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
    title="Supabase Auth 대화 API",
    description="Supabase Auth 토큰으로 현재 사용자를 확인하고 사용자별 데이터를 관리합니다.",
    version="1.0.0",
)


def public_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


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


class ProfileUpdate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


def one_or_404(rows: list[dict], detail: str) -> dict:
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


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


def upsert_profile(user_id: str, email: str, display_name: str) -> dict:
    result = (
        admin_client()
        .table("profiles")
        .upsert({
            "id": user_id,
            "email": email,
            "display_name": display_name,
        })
        .execute()
    )
    return one_or_404(result.data, "프로필을 저장하지 못했습니다")


def get_owned_conversation(conversation_id: str, user_id: str) -> dict:
    result = (
        admin_client()
        .table("chat_conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("owner_id", user_id)
        .limit(1)
        .execute()
    )
    return one_or_404(result.data, "대화방을 찾을 수 없습니다")


@app.get("/")
def root():
    return {"message": "Supabase Auth 대화 API", "docs": "/docs"}


@app.post("/auth/signup", response_model=AuthTokenResponse, tags=["Auth"])
def signup(data: SignupRequest):
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
    upsert_profile(user_id, data.email, data.display_name)

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


@app.get("/me", tags=["Profiles"])
def get_me(current: CurrentUser = Depends(get_current_user)):
    result = (
        admin_client()
        .table("profiles")
        .select("*")
        .eq("id", current.id)
        .limit(1)
        .execute()
    )
    return one_or_404(result.data, "프로필을 찾을 수 없습니다")


@app.patch("/me", tags=["Profiles"])
def update_me(data: ProfileUpdate, current: CurrentUser = Depends(get_current_user)):
    result = (
        admin_client()
        .table("profiles")
        .update({"display_name": data.display_name})
        .eq("id", current.id)
        .execute()
    )
    return one_or_404(result.data, "프로필을 찾을 수 없습니다")


@app.post("/conversations", status_code=201, tags=["Conversations"])
def create_conversation(
    data: ConversationCreate,
    current: CurrentUser = Depends(get_current_user),
):
    result = (
        admin_client()
        .table("chat_conversations")
        .insert({"owner_id": current.id, "title": data.title})
        .execute()
    )
    return one_or_404(result.data, "대화방을 생성하지 못했습니다")


@app.get("/conversations", tags=["Conversations"])
def list_conversations(current: CurrentUser = Depends(get_current_user)):
    result = (
        admin_client()
        .table("chat_conversations")
        .select("*")
        .eq("owner_id", current.id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations/{conversation_id}/messages", status_code=201, tags=["Messages"])
def create_message(
    conversation_id: str,
    data: MessageCreate,
    current: CurrentUser = Depends(get_current_user),
):
    get_owned_conversation(conversation_id, current.id)
    result = (
        admin_client()
        .table("chat_messages")
        .insert({
            "conversation_id": conversation_id,
            "owner_id": current.id,
            "role": data.role,
            "content": data.content,
        })
        .execute()
    )
    return one_or_404(result.data, "메시지를 저장하지 못했습니다")


@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(
    conversation_id: str,
    current: CurrentUser = Depends(get_current_user),
):
    get_owned_conversation(conversation_id, current.id)
    result = (
        admin_client()
        .table("chat_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("owner_id", current.id)
        .order("created_at")
        .execute()
    )
    return result.data
