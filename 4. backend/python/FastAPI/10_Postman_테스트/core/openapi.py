from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from core.config import tags_metadata


def setup_custom_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            summary=app.summary,
            description=app.description,
            routes=app.routes,
            tags=tags_metadata,
        )

        schema["components"]["securitySchemes"] = {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }

        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
