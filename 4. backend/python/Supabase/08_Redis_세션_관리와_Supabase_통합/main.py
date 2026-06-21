"""
5교시 실습: Supabase Auth + Redis 세션 + Supabase 대화 이력 통합

실행:
  docker compose up -d
  docker compose exec redis redis-cli ping
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

# 필수 Supabase 값은 누락 시 즉시 실패시키고, 실습용 TTL 값에는 기본값을 둡니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
RECENT_HISTORY_LIMIT = int(os.getenv("RECENT_HISTORY_LIMIT", "20"))
RECENT_HISTORY_TTL_SECONDS = int(os.getenv("RECENT_HISTORY_TTL_SECONDS", "86400"))

# 문자열 기반 JSON 처리와 비교를 위해 Redis 응답을 bytes가 아닌 str로 받습니다.
r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(
    title="Supabase + Redis 통합 대화 API",
    description="Auth, 앱 세션, 영구 대화 이력, 최근 대화 캐시를 통합합니다.",
    version="1.0.0",
)


def public_client() -> Client:
    # 회원가입, 로그인, 토큰 검증은 공개용 anon 키로 Supabase Auth를 호출합니다.
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    # service_role은 RLS를 우회하므로 서버 내부에서만 사용해야 합니다.
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# 요청 및 응답 데이터 모델
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


# Redis 키 형식을 한곳에서 관리해 도메인별 키가 섞이지 않게 합니다.
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
    # Auth의 user_id를 profiles의 PK로 사용해 인증 사용자와 프로필을 1:1로 연결합니다.
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
    return one_or_404(result.data, "프로필 저장에 실패했습니다")


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


def get_owned_conversation(conversation_id: str, user_id: str) -> dict:
    # admin_client는 RLS를 우회하므로 모든 조회에 owner_id 조건을 직접 적용합니다.
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
    # 오래된 메시지부터 읽을 수 있도록 List 오른쪽에 JSON 문자열을 추가합니다.
    r.rpush(key, json.dumps(message, ensure_ascii=False))
    # LTRIM으로 최근 N개만 남기고, 캐시 자체에도 별도 TTL을 적용합니다.
    r.ltrim(key, -RECENT_HISTORY_LIMIT, -1)
    r.expire(key, RECENT_HISTORY_TTL_SECONDS)


# 상태 확인 API
@app.get("/")
def root():
    return {"message": "Supabase + Redis 통합 대화 API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"redis": r.ping(), "supabase_url": SUPABASE_URL}


# 인증 API: Supabase Auth로 신원을 확인하고 Redis로 앱 세션을 관리합니다.
@app.post("/auth/signup", response_model=SignupResponse, tags=["Auth"])
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
    # 2. Auth 사용자 ID와 같은 ID로 영구 프로필을 저장합니다.
    upsert_profile(user_id, data.email, data.display_name)

    return SignupResponse(
        user_id=user_id,
        email=data.email,
        email_confirm_required=result.session is None,
    )


@app.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
def login(data: LoginRequest):
    # Supabase가 이메일과 비밀번호를 검증하면 access/refresh token을 발급합니다.
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


@app.post("/auth/logout", tags=["Auth"])
def logout(session: AppSession = Depends(get_current_session)):
    # 앱 세션 키를 삭제하면 이후 같은 session_id 요청은 401이 됩니다.
    deleted = r.delete(app_session_key(session.session_id))
    return {"session_id": session.session_id, "deleted": bool(deleted)}


# 영구 데이터 API: 원본 데이터는 Supabase PostgreSQL에 저장합니다.
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
    # service_role 조회 전에 대화방 소유권을 애플리케이션에서 확인합니다.
    get_owned_conversation(conversation_id, session.user_id)
    # 1. 원본 메시지를 Supabase에 먼저 저장해 캐시 장애 시에도 복구 가능하게 합니다.
    result = (
        admin_client()
        .table("chat_messages")
        .insert({
            "conversation_id": conversation_id,
            "owner_id": session.user_id,
            "role": data.role,
            "content": data.content,
        })
        .execute()
    )
    message = one_or_404(result.data, "메시지를 저장하지 못했습니다")
    # 2. 영구 저장 성공 후 Redis의 최근 대화 캐시를 갱신합니다.
    append_recent_message(session.user_id, conversation_id, message)
    return message


@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    # 전체 대화 이력은 캐시가 아닌 Supabase에서 시간순으로 조회합니다.
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
    # LLM 컨텍스트 등에 사용할 최근 N개는 Redis에서 빠르게 조회합니다.
    get_owned_conversation(conversation_id, session.user_id)
    key = recent_history_key(session.user_id, conversation_id)
    return [json.loads(item) for item in r.lrange(key, 0, -1)]


@app.post("/conversations/{conversation_id}/recent/rebuild", tags=["Messages"])
def rebuild_recent_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    get_owned_conversation(conversation_id, session.user_id)
    # Supabase에서 최신 N개를 내림차순으로 조회합니다.
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
    # Redis List에는 오래된 메시지부터 넣기 위해 조회 결과를 뒤집습니다.
    messages = list(reversed(result.data))
    key = recent_history_key(session.user_id, conversation_id)
    # 기존 캐시를 지운 뒤 Supabase 원본으로 완전히 재생성합니다.
    r.delete(key)
    for message in messages:
        append_recent_message(session.user_id, conversation_id, message)
    return {"rebuilt": len(messages), "recent_key": key}
