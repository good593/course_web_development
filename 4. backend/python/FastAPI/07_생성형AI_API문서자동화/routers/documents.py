from fastapi import APIRouter, HTTPException

from schemas.common import ErrorResponse
from schemas.documents import (
    DocumentGenerationRequest,
    GeneratedDocumentResponse,
    GeneratedFilesResponse,
)
from services.document_workflow import (
    MissingSnapshotError,
    create_all_documents,
    create_api_docs,
    create_change_docs,
    create_postman_collection,
    create_readme,
)

# 이 라우터의 모든 엔드포인트는 /ai-docs로 시작하고 Swagger에서 AI Documents 그룹에 묶입니다.
router = APIRouter(prefix="/ai-docs", tags=["AI Documents"])

# 생성형 AI 호출이나 OpenAPI 수집 실패는 학생들이 Swagger에서 502로 확인할 수 있게 통일합니다.
GENERATION_ERRORS = {
    502: {
        "description": "OpenAPI 스펙 수집 또는 Groq 문서 생성 실패",
        "model": ErrorResponse,
    }
}


def raise_generation_error(error: RuntimeError) -> None:
    # 외부 서버 연결 실패, Groq 오류, 토큰 한도 초과를 Swagger에서 같은 502 흐름으로 확인합니다.
    raise HTTPException(status_code=502, detail=str(error))


@router.post(
    "/api-docs",
    response_model=GeneratedDocumentResponse,
    summary="API 문서 생성",
    description="OpenAPI 스펙을 Groq에 전달해 개발자용 마크다운 API 문서를 생성합니다.",
    responses=GENERATION_ERRORS,
)
def generate_api_document(request: DocumentGenerationRequest) -> dict:
    # 라우터는 HTTP 요청/응답만 담당하고, 실제 문서 생성 흐름은 service 함수에 맡깁니다.
    try:
        return create_api_docs(request.server_url)
    except RuntimeError as error:
        raise_generation_error(error)


@router.post(
    "/postman-collection",
    response_model=GeneratedDocumentResponse,
    summary="Postman Collection 생성",
    description="OpenAPI 스펙을 Postman Collection v2.1 JSON으로 변환합니다.",
    responses=GENERATION_ERRORS,
)
def generate_collection(request: DocumentGenerationRequest) -> dict:
    try:
        return create_postman_collection(request.server_url)
    except RuntimeError as error:
        raise_generation_error(error)


@router.post(
    "/readme",
    response_model=GeneratedDocumentResponse,
    summary="README 생성",
    description="OpenAPI 스펙을 기반으로 GitHub README 초안을 생성합니다.",
    responses=GENERATION_ERRORS,
)
def generate_project_readme(request: DocumentGenerationRequest) -> dict:
    try:
        return create_readme(request.server_url)
    except RuntimeError as error:
        raise_generation_error(error)


@router.post(
    "/generate-all",
    response_model=GeneratedFilesResponse,
    summary="전체 문서 생성",
    description="API 문서, Postman Collection, README를 한 번에 생성하고 스냅샷을 저장합니다.",
    responses=GENERATION_ERRORS,
)
def generate_all(request: DocumentGenerationRequest) -> dict:
    # 전체 생성은 API 문서, Postman Collection, README, 스냅샷 저장을 한 번에 실행합니다.
    try:
        return create_all_documents(request.server_url)
    except RuntimeError as error:
        raise_generation_error(error)


@router.post(
    "/changes",
    response_model=GeneratedDocumentResponse,
    summary="변경된 엔드포인트 문서화",
    description="이전 OpenAPI 스냅샷과 현재 스펙을 비교해 변경된 엔드포인트만 문서화합니다.",
    responses={
        400: {"description": "변경 비교용 스냅샷 없음", "model": ErrorResponse},
        **GENERATION_ERRORS,
    },
)
def generate_changes(request: DocumentGenerationRequest) -> dict:
    # 변경 문서화는 이전 스냅샷이 있어야 비교할 수 있으므로 400 예외를 따로 처리합니다.
    try:
        return create_change_docs(request.server_url)
    except MissingSnapshotError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise_generation_error(error)
