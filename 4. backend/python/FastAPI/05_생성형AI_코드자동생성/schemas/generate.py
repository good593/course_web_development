from pydantic import BaseModel, Field


class GenerateCodeRequest(BaseModel):
    """API 코드 생성을 요청할 때 사용하는 입력 스키마입니다."""

    requirements: str = Field(..., min_length=1, description="생성할 API 요구사항")
    thinking: bool = Field(False, description="gemma4 thinking 모드 사용 여부")
    num_predict: int = Field(8192, ge=128, le=32768, description="최대 생성 토큰 수")


class GenerateCodeResponse(BaseModel):
    """API 코드 생성 결과 응답 스키마입니다."""

    model: str
    content: str
