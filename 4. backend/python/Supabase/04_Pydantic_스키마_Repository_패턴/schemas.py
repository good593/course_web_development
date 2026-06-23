# Literal은 변수에 들어올 수 있는 문자열 값을 지정된 목록으로 제한합니다.
from typing import Literal

# BaseModel은 요청 스키마를, Field는 필드별 세부 검증 규칙을 정의합니다.
from pydantic import BaseModel, Field


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
