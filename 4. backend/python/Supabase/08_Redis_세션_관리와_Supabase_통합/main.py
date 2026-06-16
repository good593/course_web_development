"""
5교시 실습: Supabase Auth + Redis 세션 + Supabase 대화 이력 통합

실행:
  docker run --name redis-fastapi -p 6379:6379 -d redis:7
  pip install -r requirements.txt
  copy .env.example .env
  uvicorn main:app --reload
"""

import json
import os
import time
from typing import Literal
from uuid import uuid4

import redis
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
RECENT_HISTORY_LIMIT = int(os.getenv("RECENT_HISTORY_LIMIT", "20"))
RECENT_HISTORY_TTL_SECONDS = int(os.getenv("RECENT_HISTORY_TTL_SECONDS", "86400"))

r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(
    title="Supabase + Redis 통합 대화 API",
    description="Auth, 앱 세션, 영구 대화 이력, 최근 대화 캐시를 통합합니다.",
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


class SignupResponse(BaseModel):
    user_id: str
    email: str
    email_confirm_required: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class LoginResponse(BaseModel):
    session_id: str
    user_id: str
    email: str
    ttl_seconds: int


class AppSession(BaseModel):
    session_id: str
    user_id: str
    email: str
    access_token: str


class ConversationCreate(BaseModel):
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


def now_ts() -> int:
    return int(time.time())


def app_session_key(session_id: str) -> str:
    return f"app_session:{session_id}"


def recent_history_key(user_id: str, conversation_id: str) -> str:
    return f"recent_history:{user_id}:{conversation_id}"


def one_or_404(rows: list[dict], detail: str) -> dict:
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


def upsert_profile(user_id: str, email: str, display_name: str) -> dict:
    result = (
        admin_client()
        .table("profiles")
        .upsert({
            "id": user_id,
            "email": email,
            "display_name": display_name,
        })
        .select("*")
        .execute()
    )
    return one_or_404(result.data, "프로필 저장에 실패했습니다")


def create_app_session(user_id: str, email: str, access_token: str, refresh_token: str) -> LoginResponse:
    session_id = str(uuid4())
    key = app_session_key(session_id)
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
    r.expire(key, SESSION_TTL_SECONDS)
    return LoginResponse(
        session_id=session_id,
        user_id=user_id,
        email=email,
        ttl_seconds=r.ttl(key),
    )


def get_current_session(
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
) -> AppSession:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="X-Session-Id 헤더가 필요합니다")

    key = app_session_key(x_session_id)
    data = r.hgetall(key)
    if not data:
        raise HTTPException(status_code=401, detail="앱 세션이 없거나 만료되었습니다")

    try:
        auth_result = public_client().auth.get_user(data["access_token"])
    except Exception as exc:
        r.delete(key)
        raise HTTPException(status_code=401, detail="Supabase 토큰이 만료되었거나 유효하지 않습니다") from exc

    if not auth_result.user or str(auth_result.user.id) != data["user_id"]:
        r.delete(key)
        raise HTTPException(status_code=401, detail="세션 사용자 정보가 일치하지 않습니다")

    r.hset(key, "last_seen_at", now_ts())
    r.expire(key, SESSION_TTL_SECONDS)

    return AppSession(
        session_id=x_session_id,
        user_id=data["user_id"],
        email=data["email"],
        access_token=data["access_token"],
    )


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


def append_recent_message(user_id: str, conversation_id: str, message: dict) -> None:
    key = recent_history_key(user_id, conversation_id)
    r.rpush(key, json.dumps(message, ensure_ascii=False))
    r.ltrim(key, -RECENT_HISTORY_LIMIT, -1)
    r.expire(key, RECENT_HISTORY_TTL_SECONDS)


@app.get("/")
def root():
    return {"message": "Supabase + Redis 통합 대화 API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"redis": r.ping(), "supabase_url": SUPABASE_URL}


@app.post("/auth/signup", response_model=SignupResponse, tags=["Auth"])
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

    return SignupResponse(
        user_id=user_id,
        email=data.email,
        email_confirm_required=result.session is None,
    )


@app.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
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

    return create_app_session(
        user_id=str(result.user.id),
        email=result.user.email or data.email,
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
    )


@app.post("/auth/logout", tags=["Auth"])
def logout(session: AppSession = Depends(get_current_session)):
    deleted = r.delete(app_session_key(session.session_id))
    return {"session_id": session.session_id, "deleted": bool(deleted)}


@app.get("/me", tags=["Profiles"])
def me(session: AppSession = Depends(get_current_session)):
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
        "session_ttl_seconds": r.ttl(app_session_key(session.session_id)),
    }


@app.post("/conversations", status_code=201, tags=["Conversations"])
def create_conversation(
    data: ConversationCreate,
    session: AppSession = Depends(get_current_session),
):
    result = (
        admin_client()
        .table("chat_conversations")
        .insert({"owner_id": session.user_id, "title": data.title})
        .select("*")
        .execute()
    )
    return one_or_404(result.data, "대화방을 생성하지 못했습니다")


@app.get("/conversations", tags=["Conversations"])
def list_conversations(session: AppSession = Depends(get_current_session)):
    result = (
        admin_client()
        .table("chat_conversations")
        .select("*")
        .eq("owner_id", session.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations/{conversation_id}/messages", status_code=201, tags=["Messages"])
def create_message(
    conversation_id: str,
    data: MessageCreate,
    session: AppSession = Depends(get_current_session),
):
    get_owned_conversation(conversation_id, session.user_id)
    result = (
        admin_client()
        .table("chat_messages")
        .insert({
            "conversation_id": conversation_id,
            "owner_id": session.user_id,
            "role": data.role,
            "content": data.content,
        })
        .select("*")
        .execute()
    )
    message = one_or_404(result.data, "메시지를 저장하지 못했습니다")
    append_recent_message(session.user_id, conversation_id, message)
    return message


@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    get_owned_conversation(conversation_id, session.user_id)
    result = (
        admin_client()
        .table("chat_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("owner_id", session.user_id)
        .order("created_at")
        .execute()
    )
    return result.data


@app.get("/conversations/{conversation_id}/recent", tags=["Messages"])
def recent_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    get_owned_conversation(conversation_id, session.user_id)
    key = recent_history_key(session.user_id, conversation_id)
    return [json.loads(item) for item in r.lrange(key, 0, -1)]


@app.post("/conversations/{conversation_id}/recent/rebuild", tags=["Messages"])
def rebuild_recent_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    get_owned_conversation(conversation_id, session.user_id)
    result = (
        admin_client()
        .table("chat_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("owner_id", session.user_id)
        .order("created_at", desc=True)
        .limit(RECENT_HISTORY_LIMIT)
        .execute()
    )
    messages = list(reversed(result.data))
    key = recent_history_key(session.user_id, conversation_id)
    r.delete(key)
    for message in messages:
        append_recent_message(session.user_id, conversation_id, message)
    return {"rebuilt": len(messages), "recent_key": key}
