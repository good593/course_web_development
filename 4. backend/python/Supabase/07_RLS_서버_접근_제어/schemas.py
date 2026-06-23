from typing import Literal

from pydantic import BaseModel, EmailStr, Field


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
