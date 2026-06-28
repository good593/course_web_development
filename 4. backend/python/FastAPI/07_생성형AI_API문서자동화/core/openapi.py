from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from core.metadata import TAGS_METADATA


def custom_openapi(app: FastAPI) -> dict:
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

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    app.openapi_schema = schema
    return schema
