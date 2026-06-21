import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import Client, create_client

# .env 파일의 Supabase 접속 정보를 현재 프로세스의 환경변수로 불러옵니다.
load_dotenv()

# anon key는 Auth 요청에, service_role key는 신뢰할 수 있는 서버의 DB 작업에 사용합니다.
# service_role key는 RLS를 우회하므로 브라우저나 앱 클라이언트에 절대 노출하면 안 됩니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Authorization: Bearer {token} 헤더에서 JWT를 추출하는 FastAPI 보안 스키마입니다.
# Depends()와 함께 사용하면 Swagger UI에도 Authorize 버튼이 표시됩니다.
security = HTTPBearer()

app = FastAPI(
    title="Supabase Auth 대화 API",
    description="Supabase Auth 토큰으로 현재 사용자를 확인하고 사용자별 데이터를 관리합니다.",
    version="1.0.0",
)


def public_client() -> Client:
    """anon key로 회원가입, 로그인, JWT 사용자 조회를 수행합니다."""

    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    """service_role key로 서버 측 DB 작업을 수행합니다."""

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ── Pydantic 요청/응답 스키마 ──────────────────────────────────────────

class SignupRequest(BaseModel):
    # 형식이나 길이가 맞지 않으면 엔드포인트 실행 전에 FastAPI가 422를 반환합니다.
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class AuthTokenResponse(BaseModel):
    """회원가입과 로그인이 공통으로 사용하는 인증 응답 형식입니다."""

    user_id: str
    email: str
    # Confirm email이 켜져 있으면 회원가입 직후 세션이 없어 토큰이 None일 수 있습니다.
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    email_confirm_required: bool = False


class CurrentUser(BaseModel):
    """검증된 JWT에서 얻은 현재 사용자의 최소 정보입니다."""

    id: str
    email: str


class ProfileUpdate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)


class ConversationCreate(BaseModel):
    # title을 생략하면 기본값인 "새 대화"를 사용합니다.
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    # Literal을 사용하여 정의되지 않은 메시지 역할이 저장되지 않도록 제한합니다.
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)


# ── 인증 및 DB 헬퍼 ────────────────────────────────────────────────────

def one_or_404(rows: list[dict], detail: str) -> dict:
    """Supabase 결과의 첫 행을 반환하고, 결과가 없으면 404로 변환합니다."""

    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Bearer 토큰을 Supabase Auth로 검증하고 현재 사용자를 반환합니다."""

    # HTTPBearer가 "Bearer " 접두사를 제거하므로 실제 JWT 문자열만 남습니다.
    # 헤더가 없으면 이 함수가 실행되기 전에 HTTPBearer가 요청을 거부합니다.
    token = credentials.credentials
    try:
        # 토큰의 서명과 만료 시간을 확인하고 토큰 소유자를 가져옵니다.
        result = public_client().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    # SDK 호출은 성공했지만 사용자 정보가 없는 경우도 인증 실패로 처리합니다.
    if not result.user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")

    # 엔드포인트가 Supabase SDK 응답 구조에 직접 의존하지 않도록 변환합니다.
    return CurrentUser(
        id=str(result.user.id),
        email=result.user.email or "",
    )


def upsert_profile(user_id: str, email: str, display_name: str) -> dict:
    """Auth 사용자와 1:1로 연결되는 public.profiles 행을 저장합니다."""

    # upsert는 같은 id가 있으면 수정하고, 없으면 새 행을 추가합니다.
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
    """현재 사용자가 소유한 대화방을 조회하고, 아니면 404를 반환합니다."""

    # admin_client는 RLS를 우회하므로 id만 조회하면 다른 사용자의 방도 반환됩니다.
    # 반드시 owner_id 조건을 함께 적용하여 서버에서 소유권을 검사해야 합니다.
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


# ── 엔드포인트 ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    """서버 동작 여부와 Swagger UI 경로를 안내합니다."""

    return {"message": "Supabase Auth 대화 API", "docs": "/docs"}


@app.post("/auth/signup", response_model=AuthTokenResponse, tags=["Auth"])
def signup(data: SignupRequest):
    """Supabase Auth 계정과 서비스용 프로필을 함께 생성합니다."""

    try:
        # Auth 작업은 클라이언트에도 공개할 수 있는 anon key로 수행합니다.
        # display_name은 Auth 사용자의 user_metadata에도 함께 저장합니다.
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
    # auth.users에는 인증 정보가, public.profiles에는 서비스용 정보가 저장됩니다.
    # 두 테이블은 같은 사용자 UUID를 사용하여 1:1로 연결됩니다.
    upsert_profile(user_id, data.email, data.display_name)

    # Confirm email이 꺼져 있으면 세션과 토큰이 즉시 발급됩니다.
    # 켜져 있으면 이메일 확인 전까지 session이 None입니다.
    session = result.session
    return AuthTokenResponse(
        user_id=user_id,
        email=data.email,
        # 세션이 없는 정상 회원가입도 처리할 수 있도록 조건부로 토큰을 읽습니다.
        access_token=session.access_token if session else None,
        refresh_token=session.refresh_token if session else None,
        email_confirm_required=session is None,
    )


@app.post("/auth/login", response_model=AuthTokenResponse, tags=["Auth"])
def login(data: LoginRequest):
    """이메일과 비밀번호를 확인하고 새 인증 세션을 발급합니다."""

    try:
        result = public_client().auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다") from exc

    if not result.user or not result.session:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다")

    # access_token은 API 인증에, refresh_token은 access_token 갱신에 사용합니다.
    return AuthTokenResponse(
        user_id=str(result.user.id),
        email=result.user.email or data.email,
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
    )


@app.get("/me", tags=["Profiles"])
def get_me(current: CurrentUser = Depends(get_current_user)):
    """인증된 현재 사용자의 프로필만 조회합니다."""

    # service_role 조회이므로 현재 사용자의 UUID를 id 조건으로 반드시 제한합니다.
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
    """인증된 현재 사용자의 표시 이름만 수정합니다."""

    # 요청에서 사용자 id를 받지 않고 JWT로 확인한 current.id를 사용합니다.
    # 따라서 다른 사용자의 id를 넣어 프로필을 수정할 수 없습니다.
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
    """현재 사용자를 소유자로 지정하여 새 대화방을 생성합니다."""

    # owner_id를 요청 본문에서 받지 않고 검증된 JWT 사용자 id로 강제합니다.
    result = (
        admin_client()
        .table("chat_conversations")
        .insert({"owner_id": current.id, "title": data.title})
        .execute()
    )
    return one_or_404(result.data, "대화방을 생성하지 못했습니다")


@app.get("/conversations", tags=["Conversations"])
def list_conversations(current: CurrentUser = Depends(get_current_user)):
    """현재 사용자가 소유한 대화방 목록만 반환합니다."""

    # service_role은 모든 행을 읽을 수 있으므로 owner_id 필터가 핵심 보안 조건입니다.
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
    """현재 사용자가 소유한 대화방에 메시지를 저장합니다."""

    # 메시지를 저장하기 전에 대화방 소유권부터 확인합니다.
    # 다른 사용자의 대화방이면 존재 여부를 노출하지 않고 404를 반환합니다.
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
    """현재 사용자가 소유한 대화방의 메시지만 반환합니다."""

    # 대화방 소유권을 먼저 확인한 뒤 메시지에도 owner_id 필터를 적용합니다.
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
