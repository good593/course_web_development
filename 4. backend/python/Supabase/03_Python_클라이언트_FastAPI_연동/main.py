import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from supabase import Client, create_client

# .env 파일의 환경 변수를 현재 프로세스에 불러옵니다.
load_dotenv()

# 필수 환경 변수가 없으면 서버 시작 시 KeyError가 발생합니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Service Role Key는 관리자 권한을 가지므로 서버에서만 사용해야 합니다.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# FastAPI 애플리케이션과 Swagger 문서(/docs)에 표시할 정보를 설정합니다.
app = FastAPI(
    title="Supabase 첫 연동 실습",
    description="Supabase Python 클라이언트로 데이터를 저장하고 조회합니다.",
    version="1.0.0",
)


# ── Pydantic 스키마 ─────────────────────────────────────────────────────

# BaseModel은 요청 JSON의 자료형과 제약 조건을 검사합니다.
class UserCreate(BaseModel):
    # Field(...)의 ...은 기본값이 아니라 반드시 입력해야 하는 필수 필드라는 뜻입니다.
    # str은 입력값이 문자열이어야 한다는 타입 표기입니다.
    username: str = Field(..., min_length=2, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    user_id: str
    # title을 생략하면 기본값인 "새 대화"가 사용됩니다.
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    # Literal을 사용하면 아래 세 문자열 중 하나만 입력할 수 있습니다.
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


# ── 헬퍼 ────────────────────────────────────────────────────────────────

def first_or_404(rows: list[dict], detail: str) -> dict:
    """조회 결과의 첫 행을 반환하고, 결과가 없으면 404 오류를 발생시킵니다."""
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


# ── 엔드포인트 ──────────────────────────────────────────────────────────

# @app.get/post는 함수와 HTTP 요청 경로를 연결합니다.
# status_code는 성공 응답 코드, tags는 Swagger UI의 API 그룹을 지정합니다.
@app.get("/")
def root():
    # 서버 동작 여부와 API 문서 주소를 간단히 확인하는 엔드포인트입니다.
    return {"message": "Supabase 첫 연동 실습", "docs": "/docs"}


@app.post("/users", status_code=201, tags=["Users"])
def create_user(data: UserCreate):
    # model_dump()는 검증된 Pydantic 모델을 Supabase에 전달할 딕셔너리로 바꿉니다.
    result = (
        # table()은 대상 테이블, insert()는 새 행에 저장할 값을 지정합니다.
        supabase.table("app_users")
        # insert()는 기본적으로 생성된 행을 result.data로 반환합니다.
        .insert(data.model_dump())
        # 메서드로 만든 쿼리는 execute()를 호출해야 실제로 실행됩니다.
        .execute()
    )
    return first_or_404(result.data, "사용자가 생성되지 않았습니다")


@app.get("/users", tags=["Users"])
def list_users():
    result = (
        supabase.table("app_users")
        .select("*")
        # 최신 사용자가 먼저 오도록 생성 시각을 내림차순으로 정렬합니다.
        .order("created_at", desc=True)
        .execute()
    )
    # 실행 결과의 실제 행 목록은 result.data에 들어 있습니다. 결과가 없으면 []입니다.
    return result.data


@app.post("/conversations", status_code=201, tags=["Conversations"])
def create_conversation(data: ConversationCreate):
    # 요청 데이터를 conversations 테이블에 새 행으로 저장합니다.
    result = (
        supabase.table("conversations")
        .insert(data.model_dump())
        .execute()
    )
    return first_or_404(result.data, "대화방이 생성되지 않았습니다")


@app.get("/users/{user_id}/conversations", tags=["Conversations"])
def list_conversations(user_id: str):
    # {user_id} 값은 같은 이름의 함수 매개변수로 전달됩니다.
    result = (
        supabase.table("conversations")
        .select("*")
        # eq()는 SQL의 WHERE user_id = ... 조건에 해당합니다.
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/conversations/{conversation_id}/messages", status_code=201, tags=["Messages"])
def create_message(conversation_id: str, data: MessageCreate):
    # | 연산자로 요청 본문과 URL의 conversation_id를 하나의 딕셔너리로 합칩니다.
    payload = data.model_dump() | {"conversation_id": conversation_id}
    result = (
        supabase.table("messages")
        .insert(payload)
        .execute()
    )
    return first_or_404(result.data, "메시지가 저장되지 않았습니다")


@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(conversation_id: str):
    result = (
        supabase.table("messages")
        .select("*")
        # 특정 대화의 메시지만 조회하며, desc를 생략한 order()의 기본값은 오름차순입니다.
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return result.data
