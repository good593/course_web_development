"""Swagger 실습에서 호출하는 FastAPI 엔드포인트를 모아 둔 라우터입니다."""

from fastapi import APIRouter, HTTPException
from ollama import ResponseError

from schemas.generate import GenerateCodeRequest, GenerateCodeResponse
from services.code_generator import generate_api_code
from settings import CODE_MODEL

# tags 값은 Swagger UI에서 엔드포인트를 묶어 보여 줄 때 사용됩니다.
router = APIRouter(tags=["Code Generation"])


@router.get("/")
def read_root() -> dict[str, str]:
    """서버 상태와 사용 모델을 확인합니다."""
    # README 실습 1에서 서버가 켜졌는지, 어떤 모델을 쓰는지 확인하는 응답입니다.
    return {
        "status": "ok",
        "model": CODE_MODEL,
        "docs": "/docs",
    }


@router.post("/generate", response_model=GenerateCodeResponse)
def generate_code_endpoint(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """요구사항을 받아 FastAPI 코드 초안을 생성합니다."""
    try:
        # Pydantic이 검증한 request 값을 서비스 계층으로 넘겨 Ollama 호출을 수행합니다.
        content = generate_api_code(
            request.requirements,
            thinking=request.thinking,
            num_predict=request.num_predict,
        )
    except ResponseError as error:
        # Ollama 서버가 꺼져 있거나 모델이 없으면 수업자가 원인을 알아볼 수 있게 502로 바꿉니다.
        raise HTTPException(
            status_code=502,
            detail="Ollama 호출에 실패했습니다. Ollama 실행 상태와 모델 설치 여부를 확인하세요.",
        ) from error

    # response_model 덕분에 Swagger 응답 모양은 model/content 두 필드로 고정됩니다.
    return GenerateCodeResponse(model=CODE_MODEL, content=content)
