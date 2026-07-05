from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(800, ge=1, le=4096)

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
    reply: str
    model: str
    elapsed_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
