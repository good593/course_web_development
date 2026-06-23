from typing import Literal

from pydantic import BaseModel, Field


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
