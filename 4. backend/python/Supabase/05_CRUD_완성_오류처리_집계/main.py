import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from supabase import Client, create_client

# .env의 설정값을 os.environ에 넣어 URL과 비밀 키를 코드에 직접 작성하지 않게 한다.
load_dotenv()

# os.environ[이름]은 값이 없을 때 즉시 KeyError를 내므로 잘못된 설정으로 실행되지 않는다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
# service role 키는 서버 전용 비밀 키이므로 브라우저나 공개 저장소에 노출하면 안 된다.
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def get_supabase() -> Client:
    """Depends가 호출할 Supabase 클라이언트 생성 함수다."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


app = FastAPI(
    title="FastAPI + Supabase 서비스 API",
    description="Supabase를 데이터 저장소로 사용하는 사용자별 대화 API",
    version="1.0.0",
)


# ── 스키마 ─────────────────────────────────────────────────────────────
# BaseModel은 요청 JSON을 파이썬 객체로 변환하고, 타입이나 Field 조건이 맞지 않으면
# 엔드포인트 함수를 실행하기 전에 FastAPI가 422 응답을 반환하게 한다.

class UserCreate(BaseModel):
    # Field(...)의 ...은 기본값이 없다는 뜻이므로 두 필드 모두 요청 본문에 필수다.
    # min_length와 max_length를 벗어난 문자열도 요청 검증 단계에서 거부된다.
    username: str = Field(..., min_length=2, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)


class UserUpdate(BaseModel):
    # default=None이므로 PATCH 요청에서 display_name을 생략할 수 있다.
    # 단, 생략과 {"display_name": null}은 다르다. exclude_unset=True는 생략한 필드만
    # 제외하므로 null을 직접 보내면 payload에 None이 포함된다.
    display_name: str | None = Field(default=None, min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    # title을 생략하면 기본값 "새 대화"를 사용하고, 보내면 길이를 검증한다.
    title: str = Field("새 대화", min_length=1, max_length=100)


class ConversationUpdate(BaseModel):
    # 현재 수정 가능한 값은 title 하나이며, 이 PATCH 요청에서는 반드시 보내야 한다.
    title: str = Field(..., min_length=1, max_length=100)


class MessageCreate(BaseModel):
    # Literal로 허용값을 나열했기 때문에 그 밖의 role은 422 응답으로 거부된다.
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatSummary(BaseModel):
    # summary 엔드포인트의 response_model로 사용해 응답 형식도 검증하고 문서화한다.
    user_id: str
    conversation_count: int
    message_count: int


# ── Repository ─────────────────────────────────────────────────────────
# table(), select(), eq(), order() 등은 쿼리를 조립하고 execute()가 실제 요청을 보낸다.
# 실행 결과의 data에는 조회되거나 생성·수정된 행이 list[dict] 형태로 담긴다.

class SupabaseRepository:
    """엔드포인트에서 DB 조회 코드와 공통 오류 처리를 분리한다."""

    def __init__(self, db: Client):
        self.db = db

    def one_or_404(self, rows: list[dict], detail: str) -> dict:
        """결과가 없는 경우를 모든 단건 작업에서 같은 방식으로 처리한다."""
        if not rows:
            raise HTTPException(status_code=404, detail=detail)
        return rows[0]

    def create_user(self, data: UserCreate) -> dict:
        result = (
            self.db.table("app_users")
            .insert(data.model_dump())
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

    def update_user(self, user_id: str, data: UserUpdate) -> dict:
        # model_dump()만 쓰면 생략한 display_name도 기본값 None으로 포함된다.
        # exclude_unset=True는 JSON에 없던 필드를 빼서 그 필드의 기존 값 덮어쓰기를 막는다.
        payload = data.model_dump(exclude_unset=True)
        # 빈 JSON 객체 {}처럼 수정할 필드가 하나도 없으면 불필요한 UPDATE를 실행하지 않는다.
        if not payload:
            raise HTTPException(status_code=400, detail="수정할 값이 없습니다")
        result = (
            self.db.table("app_users")
            .update(payload)
            .eq("id", user_id)
            # supabase-py 2.x는 수정된 행을 result.data에 반환하므로 select를 덧붙이지 않는다.
            .execute()
        )
        return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")

    def create_conversation(self, user_id: str, data: ConversationCreate) -> dict:
        # 먼저 부모 사용자를 조회해야 존재하지 않는 user_id에 명확한 404를 반환할 수 있다.
        self.get_user(user_id)
        # 요청 본문에는 없는 URL의 user_id를 | 연산자로 합쳐 외래 키로 저장한다.
        payload = data.model_dump() | {"user_id": user_id}
        result = (
            self.db.table("conversations")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "대화방이 생성되지 않았습니다")

    def list_conversations(self, user_id: str) -> list[dict]:
        # 대화방이 0개인 사용자와 존재하지 않는 사용자를 구분하기 위해 먼저 조회한다.
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

    def update_conversation(self, conversation_id: str, data: ConversationUpdate) -> dict:
        # 수정 필드가 title 하나이고 스키마에서 필수이므로 여기서는 exclude_unset이 필요 없다.
        result = (
            self.db.table("conversations")
            .update(data.model_dump())
            .eq("id", conversation_id)
            .execute()
        )
        return self.one_or_404(result.data, "대화방을 찾을 수 없습니다")

    def create_message(self, conversation_id: str, data: MessageCreate) -> dict:
        # 먼저 부모 대화방을 조회해야 잘못된 conversation_id에 명확한 404를 반환할 수 있다.
        self.get_conversation(conversation_id)
        # URL의 conversation_id를 요청 데이터와 합쳐 메시지의 외래 키로 저장한다.
        payload = data.model_dump() | {"conversation_id": conversation_id}
        result = (
            self.db.table("messages")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "메시지가 저장되지 않았습니다")

    def list_messages(self, conversation_id: str, limit: int) -> list[dict]:
        # 메시지가 0개인 대화방과 존재하지 않는 대화방을 구분하기 위해 먼저 조회한다.
        self.get_conversation(conversation_id)
        result = (
            self.db.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            # order()의 기본값은 오름차순이므로 오래된 메시지부터 limit개를 가져온다.
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return result.data

    def summary(self, user_id: str) -> ChatSummary:
        # list_conversations()를 재사용해 사용자 존재 확인과 대화방 조회를 함께 처리한다.
        conversations = self.list_conversations(user_id)
        message_count = 0
        for conversation in conversations:
            # 메시지 내용은 필요 없으므로 id만 받고, 반환된 행의 길이로 개수를 센다.
            # 학습을 위한 단순한 방식이며 대화방 수만큼 메시지 조회 쿼리가 실행된다.
            result = (
                self.db.table("messages")
                .select("id")
                .eq("conversation_id", conversation["id"])
                .execute()
            )
            message_count += len(result.data)
        return ChatSummary(
            user_id=user_id,
            conversation_count=len(conversations),
            message_count=message_count,
        )


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    """FastAPI가 get_supabase를 호출해 만든 db로 Repository를 조립한다."""
    return SupabaseRepository(db)


# ── 엔드포인트 ─────────────────────────────────────────────────────────
# @app.get/post/patch는 함수가 처리할 HTTP 메서드와 URL을 FastAPI에 등록한다.
# 경로의 {이름}은 같은 이름의 함수 인자로, BaseModel 타입은 요청 본문으로 해석된다.
# Depends(get_repo)는 엔드포인트가 호출될 때 FastAPI가 repo를 만들어 전달하게 한다.
# tags는 Swagger 문서의 그룹을, status_code는 성공 응답의 상태 코드를 지정한다.
# 생성 API의 201은 요청이 성공했고 새 자원이 만들어졌다는 의미다.

@app.get("/")
def root():
    return {"message": "FastAPI + Supabase 서비스 API", "docs": "/docs"}


@app.post("/users", status_code=201, tags=["Users"])
def create_user(data: UserCreate, repo: SupabaseRepository = Depends(get_repo)):
    return repo.create_user(data)


@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.get_user(user_id)


# app.patch()가 HTTP 메서드를 PATCH로 정하고, 부분 수정 동작은 update_user() 안의
# exclude_unset=True가 요청에서 생략한 필드를 UPDATE 대상에서 제외해 구현한다.
@app.patch("/users/{user_id}", tags=["Users"])
def update_user(user_id: str, data: UserUpdate, repo: SupabaseRepository = Depends(get_repo)):
    return repo.update_user(user_id, data)


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


@app.patch("/conversations/{conversation_id}", tags=["Conversations"])
def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.update_conversation(conversation_id, data)


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
    # Query()를 사용했으므로 limit는 ?limit=20 형태의 쿼리 파라미터가 된다.
    # 생략하면 50을 쓰고, ge=1과 le=100 범위를 벗어나면 FastAPI가 422를 반환한다.
    limit: int = Query(50, ge=1, le=100),
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.list_messages(conversation_id, limit)


# response_model은 반환값을 ChatSummary 구조로 검증하며 Swagger에도 응답 형식을 표시한다.
@app.get("/users/{user_id}/summary", response_model=ChatSummary, tags=["Users"])
def get_summary(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.summary(user_id)
