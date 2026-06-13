"""
4교시 실습: Supabase Python 클라이언트와 FastAPI 첫 연동

실행:
  pip install -r requirements.txt
  copy .env.example .env
  # .env 파일에 SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 입력
  uvicorn main:app --reload
"""

import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

app = FastAPI(
    title="Supabase 첫 연동 실습",
    description="Supabase Python 클라이언트로 데이터를 저장하고 조회합니다.",
    version="1.0.0",
)


# ── Pydantic 스키마 ─────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    user_id: str
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


# ── 헬퍼 ────────────────────────────────────────────────────────────────

def first_or_404(rows: list[dict], detail: str) -> dict:
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


# ── 엔드포인트 ──────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Supabase 첫 연동 실습", "docs": "/docs"}


@app.post("/users", status_code=201, tags=["Users"])
def create_user(data: UserCreate):
    result = (
        supabase.table("app_users")
        .insert(data.model_dump())
        .select("*")
        .execute()
    )
    return first_or_404(result.data, "사용자가 생성되지 않았습니다")


@app.get("/users", tags=["Users"])
def list_users():
    result = (
        supabase.table("app_users")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations", status_code=201, tags=["Conversations"])
def create_conversation(data: ConversationCreate):
    result = (
        supabase.table("conversations")
        .insert(data.model_dump())
        .select("*")
        .execute()
    )
    return first_or_404(result.data, "대화방이 생성되지 않았습니다")


@app.get("/users/{user_id}/conversations", tags=["Conversations"])
def list_conversations(user_id: str):
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations/{conversation_id}/messages", status_code=201, tags=["Messages"])
def create_message(conversation_id: str, data: MessageCreate):
    payload = data.model_dump() | {"conversation_id": conversation_id}
    result = (
        supabase.table("messages")
        .insert(payload)
        .select("*")
        .execute()
    )
    return first_or_404(result.data, "메시지가 저장되지 않았습니다")


@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(conversation_id: str):
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return result.data
