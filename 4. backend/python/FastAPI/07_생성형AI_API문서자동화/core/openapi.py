from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from core.metadata import TAGS_METADATA


def custom_openapi(app: FastAPI) -> dict:
    """Swagger UI에 표시할 OpenAPI 스키마를 수업용으로 보강합니다."""
    if app.openapi_schema:
        return app.openapi_schema

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

    app.openapi_schema = schema
    return schema
