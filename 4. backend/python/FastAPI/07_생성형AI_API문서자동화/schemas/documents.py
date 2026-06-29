from pydantic import BaseModel, Field


class DocumentGenerationRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"server_url": "http://localhost:8000"},
                {"server_url": "http://localhost:8000/openapi.json"},
            ]
        }
    }

    server_url: str = Field(
        default="http://localhost:8000",
        description="문서화할 FastAPI 서버 기본 URL 또는 openapi.json 전체 URL",
    )


class GeneratedDocumentResponse(BaseModel):
    endpoint_count: int = Field(description="OpenAPI 스펙에서 확인한 엔드포인트 수")
    filename: str | None = Field(default=None, description="저장된 파일명")
    path: str | None = Field(default=None, description="저장된 파일 경로")
    content: str = Field(description="생성된 문서 본문")


class GeneratedFileInfo(BaseModel):
    filename: str
    path: str
    description: str


class GeneratedFilesResponse(BaseModel):
    endpoint_count: int
    files: list[GeneratedFileInfo]
    message: str
