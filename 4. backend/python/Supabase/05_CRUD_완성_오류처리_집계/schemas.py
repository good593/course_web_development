from typing import Literal

from pydantic import BaseModel, Field


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
