from typing import Literal

from pydantic import BaseModel, EmailStr, Field


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
    """Redis에서 복원한 앱 세션 정보입니다. 엔드포인트에서 현재 사용자로 사용합니다."""

    session_id: str
    user_id: str
    email: str
    access_token: str


class ConversationCreate(BaseModel):
    title: str = Field("새 대화", min_length=1, max_length=100)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=2000)
