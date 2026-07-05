from pydantic import BaseModel, ConfigDict, Field


class DocumentGenerationRequest(BaseModel):
    """AI 문서 생성 API가 어떤 FastAPI 서버를 문서화할지 받는 입력 스키마입니다."""

    # Swagger UI의 Example Value에 표시될 예시입니다.
    # 기본값은 README에서 실행하는 현재 서버의 주소와 같습니다.
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"server_url": "http://localhost:8001"},
                {"server_url": "http://localhost:8001/openapi.json"},
            ]
        }
    )

    server_url: str = Field(
        default="http://localhost:8001",
        description="문서화할 FastAPI 서버 기본 URL 또는 openapi.json 전체 URL",
    )


class GeneratedDocumentResponse(BaseModel):
    """문서 하나를 생성하는 API의 응답 스키마입니다."""

    # filename/path는 생성에 실패하거나 변경이 없을 때 None이 될 수 있습니다.
    endpoint_count: int = Field(description="OpenAPI 스펙에서 확인한 엔드포인트 수")
    filename: str | None = Field(default=None, description="저장된 파일명")
    path: str | None = Field(default=None, description="저장된 파일 경로")
    content: str = Field(description="생성된 문서 본문")


class GeneratedFileInfo(BaseModel):
    """여러 문서를 한 번에 생성할 때 파일별 정보를 표현합니다."""

    filename: str
    path: str
    description: str


class GeneratedFilesResponse(BaseModel):
    """문서 묶음 생성 API의 응답 스키마입니다."""

    endpoint_count: int
    files: list[GeneratedFileInfo]
    message: str
