"""Swagger의 Request/Response Body 모양을 정의하는 Pydantic 스키마입니다."""

from pydantic import BaseModel, ConfigDict, Field


class GenerateCodeRequest(BaseModel):
    """API 코드 생성을 요청할 때 사용하는 입력 스키마입니다."""

    # Swagger UI의 Example Value에 표시될 예시입니다.
    # JSON 요청 본문이므로 여러 줄 문자열은 \n 이스케이프로 표현합니다.
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "requirements": "FastAPI와 Pydantic v2를 사용해서 메모 앱 API를 만들어줘.\nPOST /memos, GET /memos, GET /memos/{memo_id}, DELETE /memos/{memo_id}를 구현하고 인메모리 dict를 사용해줘.",
                    "thinking": False,
                    "num_predict": 1024,
                }
            ]
        }
    )

    # requirements가 실제로 모델에게 전달되는 자연어 요구사항입니다.
    requirements: str = Field(..., min_length=1, description="생성할 API 요구사항")

    # true이면 services.code_generator.build_system_message()에서 thinking 토큰을 붙입니다.
    thinking: bool = Field(False, description="gemma4 thinking 모드 사용 여부")

    # Ollama가 생성할 최대 토큰 수입니다. 너무 작거나 크면 422 검증 오류가 납니다.
    num_predict: int = Field(8192, ge=128, le=32768, description="최대 생성 토큰 수")


class GenerateCodeResponse(BaseModel):
    """API 코드 생성 결과 응답 스키마입니다."""

    # 호출에 사용한 Ollama 모델 이름입니다.
    model: str

    # 모델이 생성한 FastAPI 코드 초안입니다. 보통 ```python 코드 블록 형태로 들어옵니다.
    content: str
