from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from core.metadata import TAGS_METADATA


def custom_openapi(app: FastAPI) -> dict:
    """Swagger UI에 표시할 OpenAPI 스키마를 수업용으로 보강합니다."""
    # FastAPI는 한 번 만든 OpenAPI 스키마를 캐시해 두면 매 요청마다 다시 계산하지 않습니다.
    if app.openapi_schema:
        return app.openapi_schema

    # 기본 스키마를 먼저 만들고, 아래에서 보안 스키마 이름만 수업용으로 덧붙입니다.
    schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
        tags=TAGS_METADATA,
    )

    # HTTPBearer(scheme_name="BearerAuth")와 같은 이름으로 보안 스키마를 고정합니다.
    components = schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # 완성된 스키마를 앱에 저장해야 Swagger UI와 /openapi.json이 같은 결과를 사용합니다.
    app.openapi_schema = schema
    return schema
