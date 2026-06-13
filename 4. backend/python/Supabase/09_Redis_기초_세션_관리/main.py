"""
4교시 실습: Redis 기반 세션 관리와 임시 대화 이력

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
from pydantic import BaseModel, Field

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))
CHAT_HISTORY_TTL_SECONDS = int(os.getenv("CHAT_HISTORY_TTL_SECONDS", "86400"))

r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(
    title="Redis 세션 관리 API",
    description="Redis Hash, List, TTL로 사용자 상태와 대화 이력을 관리합니다.",
    version="1.0.0",
)


class SessionCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=50)


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    display_name: str
    status: str
    ttl_seconds: int


class StatusUpdate(BaseModel):
    status: Literal["online", "away", "busy"]


class ChatMessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


def now_ts() -> int:
    return int(time.time())


def session_key(session_id: str) -> str:
    return f"session:{session_id}"


def history_key(session_id: str) -> str:
    return f"chat_history:{session_id}"


def get_session(
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
) -> dict:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="X-Session-Id 헤더가 필요합니다")

    key = session_key(x_session_id)
    data = r.hgetall(key)
    if not data:
        raise HTTPException(status_code=401, detail="세션이 없거나 만료되었습니다")

    r.hset(key, "last_seen_at", now_ts())
    r.expire(key, SESSION_TTL_SECONDS)
    data["session_id"] = x_session_id
    return data


@app.get("/")
def root():
    return {"message": "Redis 세션 관리 API", "docs": "/docs"}


@app.get("/redis/health")
def redis_health():
    return {"ok": r.ping(), "redis_url": REDIS_URL}


@app.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(data: SessionCreate):
    session_id = str(uuid4())
    key = session_key(session_id)

    r.hset(
        key,
        mapping={
            "user_id": data.user_id,
            "display_name": data.display_name,
            "status": "online",
            "created_at": now_ts(),
            "last_seen_at": now_ts(),
        },
    )
    r.expire(key, SESSION_TTL_SECONDS)

    return SessionResponse(
        session_id=session_id,
        user_id=data.user_id,
        display_name=data.display_name,
        status="online",
        ttl_seconds=r.ttl(key),
    )


@app.get("/sessions/me")
def get_my_session(session: dict = Depends(get_session)):
    return {
        **session,
        "ttl_seconds": r.ttl(session_key(session["session_id"])),
    }


@app.patch("/sessions/me/status")
def update_status(data: StatusUpdate, session: dict = Depends(get_session)):
    key = session_key(session["session_id"])
    r.hset(key, mapping={"status": data.status, "last_seen_at": now_ts()})
    r.expire(key, SESSION_TTL_SECONDS)
    return {"session_id": session["session_id"], "status": data.status}


@app.delete("/sessions/me")
def delete_session(session: dict = Depends(get_session)):
    session_id = session["session_id"]
    deleted = r.delete(session_key(session_id), history_key(session_id))
    return {"session_id": session_id, "deleted_keys": deleted}


@app.post("/chat/messages", status_code=201)
def add_chat_message(data: ChatMessageCreate, session: dict = Depends(get_session)):
    key = history_key(session["session_id"])
    message = {
        "role": data.role,
        "content": data.content,
        "created_at": now_ts(),
    }
    r.rpush(key, json.dumps(message, ensure_ascii=False))
    r.ltrim(key, -50, -1)
    r.expire(key, CHAT_HISTORY_TTL_SECONDS)
    return message | {"history_length": r.llen(key)}


@app.get("/chat/messages")
def list_chat_messages(session: dict = Depends(get_session)):
    key = history_key(session["session_id"])
    raw_items = r.lrange(key, 0, -1)
    return [json.loads(item) for item in raw_items]


@app.get("/metrics")
def metrics():
    session_count = sum(1 for _ in r.scan_iter("session:*"))
    history_count = sum(1 for _ in r.scan_iter("chat_history:*"))
    return {
        "session_keys": session_count,
        "chat_history_keys": history_count,
        "db_size": r.dbsize(),
    }
