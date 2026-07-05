"""
채팅 API가 주고받는 데이터 모양을 정의합니다.

Pydantic 모델을 사용하면 FastAPI가 요청 검증과 Swagger 예시 생성을 자동으로 도와줍니다.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    # 대화 기록에 저장되는 한 개의 메시지입니다.
    # role은 OpenAI/Groq 채팅 API가 이해하는 값만 허용합니다.
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    # 사용자가 방금 입력한 질문입니다.
    message: str = Field(..., min_length=1, max_length=2000)
    # 이전 대화 목록입니다. 너무 길어지지 않도록 최대 20개로 제한합니다.
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    # temperature는 답변의 창의성 정도입니다. 0에 가까울수록 안정적입니다.
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    # max_tokens는 모델이 생성할 답변 길이의 상한입니다.
    max_tokens: int = Field(800, ge=1, le=4096)

    # Swagger UI의 Request body 예시로 표시됩니다.
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Streamlit과 FastAPI를 분리하면 어떤 장점이 있어?",
                    "history": [],
                    "temperature": 0.7,
                    "max_tokens": 800,
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    # FastAPI가 /chat 응답을 이 모양으로 맞춰서 JSON으로 반환합니다.
    reply: str
    model: str
    elapsed_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
