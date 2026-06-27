from fastapi import APIRouter, HTTPException
from ollama import ResponseError

from schemas.generate import GenerateCodeRequest, GenerateCodeResponse
from services.code_generator import generate_api_code
from settings import CODE_MODEL

router = APIRouter(tags=["Code Generation"])


@router.get("/")
def read_root() -> dict[str, str]:
    """서버 상태와 사용 모델을 확인합니다."""
    return {
        "status": "ok",
        "model": CODE_MODEL,
        "docs": "/docs",
    }


@router.post("/generate", response_model=GenerateCodeResponse)
def generate_code_endpoint(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """요구사항을 받아 FastAPI 코드 초안을 생성합니다."""
    try:
        content = generate_api_code(
            request.requirements,
            thinking=request.thinking,
            num_predict=request.num_predict,
        )
    except ResponseError as error:
        raise HTTPException(
            status_code=502,
            detail="Ollama 호출에 실패했습니다. Ollama 실행 상태와 모델 설치 여부를 확인하세요.",
        ) from error

    return GenerateCodeResponse(model=CODE_MODEL, content=content)
