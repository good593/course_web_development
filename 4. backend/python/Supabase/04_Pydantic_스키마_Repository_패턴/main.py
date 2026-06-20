import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


app = FastAPI(
    title="Pydantic + Repository 패턴",
    description="Field 검증과 Repository 패턴으로 코드를 구조화합니다.",
    version="1.0.0",
)


# ── Pydantic 스키마 ─────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


# ── Repository ─────────────────────────────────────────────────────────

class SupabaseRepository:
    def __init__(self, db: Client):
        self.db = db

    def one_or_404(self, rows: list[dict], detail: str) -> dict:
        if not rows:
            raise HTTPException(status_code=404, detail=detail)
        return rows[0]

    def create_user(self, data: UserCreate) -> dict:
        result = (
            self.db.table("app_users")
            .insert(data.model_dump())
            .select("*")
            .execute()
        )
        return self.one_or_404(result.data, "사용자가 생성되지 않았습니다")

    def get_user(self, user_id: str) -> dict:
        result = (
            self.db.table("app_users")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")

    def list_users(self) -> list[dict]:
        result = (
            self.db.table("app_users")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def create_conversation(self, user_id: str, data: ConversationCreate) -> dict:
        self.get_user(user_id)  # 사용자 존재 확인 — 없으면 404
        payload = data.model_dump() | {"user_id": user_id}
        result = (
            self.db.table("conversations")
            .insert(payload)
            .select("*")
            .execute()
        )
        return self.one_or_404(result.data, "대화방이 생성되지 않았습니다")

    def list_conversations(self, user_id: str) -> list[dict]:
        self.get_user(user_id)
        result = (
            self.db.table("conversations")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def get_conversation(self, conversation_id: str) -> dict:
        result = (
            self.db.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "대화방을 찾을 수 없습니다")

    def create_message(self, conversation_id: str, data: MessageCreate) -> dict:
        self.get_conversation(conversation_id)
        payload = data.model_dump() | {"conversation_id": conversation_id}
        result = (
            self.db.table("messages")
            .insert(payload)
            .select("*")
            .execute()
        )
        return self.one_or_404(result.data, "메시지가 저장되지 않았습니다")

    def list_messages(self, conversation_id: str) -> list[dict]:
        self.get_conversation(conversation_id)
        result = (
            self.db.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at")
            .execute()
        )
        return result.data


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    return SupabaseRepository(db)


# ── 엔드포인트 ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Pydantic + Repository 패턴", "docs": "/docs"}


@app.post("/users", status_code=201, tags=["Users"])
def create_user(data: UserCreate, repo: SupabaseRepository = Depends(get_repo)):
    return repo.create_user(data)


@app.get("/users", tags=["Users"])
def list_users(repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_users()


@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.get_user(user_id)


@app.post("/users/{user_id}/conversations", status_code=201, tags=["Conversations"])
def create_conversation(
    user_id: str,
    data: ConversationCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_conversation(user_id, data)


@app.get("/users/{user_id}/conversations", tags=["Conversations"])
def list_conversations(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_conversations(user_id)


@app.post("/conversations/{conversation_id}/messages", status_code=201, tags=["Messages"])
def create_message(
    conversation_id: str,
    data: MessageCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_message(conversation_id, data)


@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(
    conversation_id: str,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.list_messages(conversation_id)
