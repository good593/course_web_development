from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(500, ge=1, le=4096)
    system_instruction: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "FastAPI에서 비동기 처리가 필요한 이유를 쉽게 설명해줘.",
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "system_instruction": "너는 한국어로 친절하게 설명하는 백엔드 강사야.",
                }
            ]
        }
    }


class AskResponse(BaseModel):
    answer: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "FastAPI에서 비동기 처리를 사용하면 오래 걸리는 API 호출 중에도 서버가 다른 요청을 계속 처리할 수 있습니다.",
                    "input_tokens": 24,
                    "output_tokens": 42,
                    "total_tokens": 66,
                }
            ]
        }
    }


class SessionCreateResponse(BaseModel):
    session_id: str
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "b9d4f3b0-2b7f-4b8c-9f48-0c7d3e13d123",
                    "message": "세션이 생성되었습니다.",
                }
            ]
        }
    }


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(800, ge=1, le=4096)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "방금 설명한 내용을 쇼핑몰 서비스 예시로 다시 설명해줘.",
                    "temperature": 0.7,
                    "max_tokens": 800,
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    input_tokens: int
    output_tokens: int
    history_length: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "b9d4f3b0-2b7f-4b8c-9f48-0c7d3e13d123",
                    "reply": "쇼핑몰에서 상품 추천 API를 호출하는 동안에도 장바구니 조회 요청을 처리할 수 있는 것이 비동기 처리의 장점입니다.",
                    "input_tokens": 31,
                    "output_tokens": 53,
                    "history_length": 2,
                }
            ]
        }
    }


class HistoryMessage(BaseModel):
    role: str
    text: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "text": "FastAPI에서 스트리밍 응답은 언제 사용하면 좋아?",
                }
            ]
        }
    }


class SessionSummary(BaseModel):
    session_id: str
    created_ago_sec: int
    last_used_ago_sec: int
    history_turns: int


class StatsResponse(BaseModel):
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    active_sessions: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_requests": 5,
                    "total_input_tokens": 1320,
                    "total_output_tokens": 2480,
                    "total_tokens": 3800,
                    "estimated_cost_usd": 0.000843,
                    "active_sessions": 1,
                }
            ]
        }
    }
