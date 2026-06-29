from fastapi import FastAPI

from core.metadata import API_DESCRIPTION, API_VERSION, TAGS_METADATA, is_production
from core.openapi import custom_openapi
from routers.documents import router as documents_router
from routers.health import router as health_router
from routers.orders import router as orders_router
from routers.products import router as products_router
from routers.users import router as users_router


def create_app() -> FastAPI:
    docs_enabled = not is_production()
    app = FastAPI(
        title="생성형 AI API 문서 자동화",
        summary="FastAPI OpenAPI 스펙을 Groq로 문서화하는 실습 API",
        description=API_DESCRIPTION,
        version=API_VERSION,
        contact={"name": "API 지원팀", "email": "api@example.com"},
        license_info={"name": "MIT"},
        openapi_tags=TAGS_METADATA,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    app.include_router(health_router)
    app.include_router(products_router)
    app.include_router(orders_router)
    app.include_router(users_router)
    app.include_router(documents_router)
    app.openapi = lambda: custom_openapi(app)
    return app


app = create_app()
