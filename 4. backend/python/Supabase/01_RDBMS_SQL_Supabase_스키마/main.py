"""
1교시 실습: Supabase 테이블 저장/조회

실행:
  pip install -r requirements.txt
  copy .env.example .env
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
    title="Supabase SQL 기초 실습",
    description="RDBMS 스키마를 Supabase에 만들고 FastAPI에서 저장/조회합니다.",
    version="1.0.0",
)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    user_id: str
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


def first_or_404(rows: list[dict], detail: str) -> dict:
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


@app.get("/")
def root():
    return {"message": "Supabase SQL 기초 실습", "docs": "/docs"}


@app.post("/users", status_code=201)
def create_user(data: UserCreate):
    result = (
        supabase.table("app_users")
        .insert(data.model_dump())
        .select("*")
        .execute()
    )
    return first_or_404(result.data, "사용자가 생성되지 않았습니다")


@app.get("/users")
def list_users():
    result = (
        supabase.table("app_users")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations", status_code=201)
def create_conversation(data: ConversationCreate):
    result = (
        supabase.table("conversations")
        .insert(data.model_dump())
        .select("*")
        .execute()
    )
    return first_or_404(result.data, "대화방이 생성되지 않았습니다")


@app.get("/users/{user_id}/conversations")
def list_conversations(user_id: str):
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations/{conversation_id}/messages", status_code=201)
def create_message(conversation_id: str, data: MessageCreate):
    payload = data.model_dump() | {"conversation_id": conversation_id}
    result = (
        supabase.table("messages")
        .insert(payload)
        .select("*")
        .execute()
    )
    return first_or_404(result.data, "메시지가 저장되지 않았습니다")


@app.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: str):
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return result.data
