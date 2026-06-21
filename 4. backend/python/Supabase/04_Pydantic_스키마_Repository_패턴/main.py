# 운영체제의 환경 변수에 접근하기 위한 표준 라이브러리입니다.
import os
# Literal은 변수에 들어올 수 있는 문자열 값을 지정된 목록으로 제한합니다.
from typing import Literal

# 프로젝트 루트의 .env 파일을 읽어 환경 변수로 등록합니다.
from dotenv import load_dotenv
# Depends: 의존성 주입, FastAPI: 앱 생성, HTTPException: HTTP 오류 응답에 사용합니다.
from fastapi import Depends, FastAPI, HTTPException
# BaseModel은 요청 스키마를, Field는 필드별 세부 검증 규칙을 정의합니다.
from pydantic import BaseModel, Field
# Client는 타입 표시에, create_client는 Supabase 클라이언트 생성에 사용합니다.
from supabase import Client, create_client

# .env 파일의 값을 환경 변수로 불러옵니다.
load_dotenv()

# 환경 변수가 없으면 서버 시작 시 바로 오류가 발생하므로 설정 누락을 빠르게 알 수 있습니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def get_supabase() -> Client:
    # 요청 처리에 사용할 Supabase 클라이언트를 생성하는 의존성 함수입니다.
    # URL은 프로젝트 위치, Service Role Key는 서버의 DB 접근 권한을 전달합니다.
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# FastAPI 애플리케이션을 생성합니다. 아래 정보는 /docs와 OpenAPI 문서에도 표시됩니다.
app = FastAPI(
    title="Pydantic + Repository 패턴",
    description="Field 검증과 Repository 패턴으로 코드를 구조화합니다.",
    version="1.0.0",
)


# ── Pydantic 스키마 ─────────────────────────────────────────────────────

# 요청 본문의 형태와 검증 규칙을 정의합니다.
# 검증에 실패하면 엔드포인트가 실행되기 전에 FastAPI가 자동으로 422를 반환합니다.
class UserCreate(BaseModel):
    # ...은 필수값, min_length와 max_length는 허용할 문자열 길이입니다.
    username: str = Field(..., min_length=2, max_length=30)
    # 화면에 표시할 이름도 필수이며 1자 이상 50자 이하만 허용합니다.
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    # title을 생략하면 "새 대화"가 기본값으로 사용됩니다.
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    # Literal에 나열하지 않은 값(예: "bot")은 422 검증 오류가 됩니다.
    role: Literal["user", "assistant", "system"]
    # 빈 메시지를 막고 지나치게 긴 요청 본문도 제한합니다.
    content: str = Field(..., min_length=1, max_length=2000)


# ── Repository ─────────────────────────────────────────────────────────

# 데이터베이스 접근과 쿼리 로직을 엔드포인트에서 분리해 한곳에 모읍니다.
class SupabaseRepository:
    def __init__(self, db: Client):
        # 외부에서 클라이언트를 주입받아 실제 객체나 테스트용 객체로 교체할 수 있습니다.
        self.db = db

    def one_or_404(self, rows: list[dict], detail: str) -> dict:
        # 단건 조회 결과가 비어 있으면 일관된 형식의 404 응답을 만듭니다.
        if not rows:
            raise HTTPException(status_code=404, detail=detail)
        return rows[0]

    def create_user(self, data: UserCreate) -> dict:
        # model_dump()는 검증이 끝난 Pydantic 모델을 DB에 넣을 dict로 변환합니다.
        result = (
            # app_users 테이블에 사용자 데이터를 추가할 쿼리를 만듭니다.
            self.db.table("app_users")
            .insert(data.model_dump())
            # insert는 기본적으로 저장된 행을 반환하며, execute가 요청을 전송합니다.
            .execute()
        )
        # result.data는 행의 목록이므로 첫 번째 행을 꺼내 반환합니다.
        return self.one_or_404(result.data, "사용자가 생성되지 않았습니다")

    def get_user(self, user_id: str) -> dict:
        # 기본 키 id로 사용자 한 명을 조회합니다.
        result = (
            self.db.table("app_users")
            .select("*")
            # eq는 id가 user_id와 같은 행만 필터링합니다.
            .eq("id", user_id)
            # 단건 조회이므로 필요한 행을 최대 1개로 제한합니다.
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")

    def list_users(self) -> list[dict]:
        # 조건 없이 app_users의 모든 행을 조회합니다.
        result = (
            self.db.table("app_users")
            .select("*")
            # 최신 사용자가 먼저 보이도록 생성 시각을 내림차순 정렬합니다.
            .order("created_at", desc=True)
            .execute()
        )
        # 목록 API이므로 첫 행이 아니라 전체 행 배열을 그대로 반환합니다.
        return result.data

    def create_conversation(self, user_id: str, data: ConversationCreate) -> dict:
        # FK 오류를 그대로 노출하지 않고 친절한 404를 주기 위해 사용자를 먼저 조회합니다.
        self.get_user(user_id)
        # 요청 데이터에 URL 경로에서 받은 외래 키를 합쳐 저장할 데이터를 만듭니다.
        payload = data.model_dump() | {"user_id": user_id}
        result = (
            self.db.table("conversations")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "대화방이 생성되지 않았습니다")

    def list_conversations(self, user_id: str) -> list[dict]:
        # 존재하지 않는 사용자의 목록 요청도 빈 배열 대신 명확한 404로 응답합니다.
        self.get_user(user_id)
        result = (
            self.db.table("conversations")
            .select("*")
            # 해당 사용자가 만든 대화방만 조회합니다.
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def get_conversation(self, conversation_id: str) -> dict:
        # 대화방의 기본 키 id로 한 건만 조회합니다.
        result = (
            self.db.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "대화방을 찾을 수 없습니다")

    def create_message(self, conversation_id: str, data: MessageCreate) -> dict:
        # 메시지를 저장하기 전에 부모 대화방이 실제로 존재하는지 확인합니다.
        self.get_conversation(conversation_id)
        # 검증된 메시지 데이터에 대화방 외래 키를 추가합니다.
        payload = data.model_dump() | {"conversation_id": conversation_id}
        result = (
            self.db.table("messages")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "메시지가 저장되지 않았습니다")

    def list_messages(self, conversation_id: str) -> list[dict]:
        # 존재하지 않는 대화방의 메시지 목록 요청은 404로 처리합니다.
        self.get_conversation(conversation_id)
        result = (
            self.db.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            # 대화 흐름을 읽을 수 있도록 오래된 메시지부터 정렬합니다.
            .order("created_at")
            .execute()
        )
        return result.data


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    # FastAPI가 get_supabase()의 결과를 db에 넣고 Repository를 만들어 줍니다.
    return SupabaseRepository(db)


# ── 엔드포인트 ─────────────────────────────────────────────────────────
# 엔드포인트는 경로, 상태 코드, 요청 흐름만 담당하고 DB 작업은 Repository에 위임합니다.

# GET / 요청을 애플리케이션의 기본 안내 응답과 연결합니다.
@app.get("/")
def root():
    # 대화형 API 문서는 /docs에서 확인할 수 있습니다.
    return {"message": "Pydantic + Repository 패턴", "docs": "/docs"}


# 새 사용자를 생성하며 성공 시 HTTP 201 Created를 반환합니다.
# tags는 Swagger 문서에서 관련 API를 Users 그룹으로 묶습니다.
@app.post("/users", status_code=201, tags=["Users"])
def create_user(data: UserCreate, repo: SupabaseRepository = Depends(get_repo)):
    # Depends가 get_repo()를 호출해 현재 요청에서 사용할 Repository를 주입합니다.
    return repo.create_user(data)


# 등록된 사용자 목록을 최신순으로 조회합니다.
@app.get("/users", tags=["Users"])
def list_users(repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_users()


# 중괄호로 감싼 user_id는 URL에서 함수 인자로 전달되는 경로 매개변수입니다.
@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.get_user(user_id)


# 특정 사용자의 대화방을 생성합니다. data는 요청 본문에서 자동 변환됩니다.
@app.post("/users/{user_id}/conversations", status_code=201, tags=["Conversations"])
def create_conversation(
    user_id: str,
    data: ConversationCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_conversation(user_id, data)


# 특정 사용자가 가진 대화방 목록을 최신순으로 조회합니다.
@app.get("/users/{user_id}/conversations", tags=["Conversations"])
def list_conversations(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_conversations(user_id)


# 특정 대화방에 검증된 역할과 내용으로 새 메시지를 저장합니다.
@app.post("/conversations/{conversation_id}/messages", status_code=201, tags=["Messages"])
def create_message(
    conversation_id: str,
    data: MessageCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_message(conversation_id, data)


# 특정 대화방의 메시지를 생성 시각 순서대로 조회합니다.
@app.get("/conversations/{conversation_id}/messages", tags=["Messages"])
def list_messages(
    conversation_id: str,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.list_messages(conversation_id)
