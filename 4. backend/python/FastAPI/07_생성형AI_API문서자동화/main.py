"""
FastAPI OpenAPI 스펙을 생성형 AI로 문서화하는 실습 서버입니다.

실행 전 `.env` 파일에 Groq API 키를 준비하세요.

    GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxx
"""

from fastapi import FastAPI

from core.metadata import API_DESCRIPTION, API_VERSION, TAGS_METADATA, is_production
from core.openapi import custom_openapi
from routers.documents import router as documents_router
from routers.health import router as health_router
from routers.orders import router as orders_router
from routers.products import router as products_router
from routers.users import router as users_router


def create_app() -> FastAPI:
    """README의 서버 실행 및 Swagger 실습에서 사용하는 FastAPI 앱을 만듭니다."""
    # 운영 환경에서는 문서 화면을 숨기고, 개발/수업 환경에서만 Swagger UI를 켭니다.
    docs_enabled = not is_production()

    # title, description, tags 같은 값은 /openapi.json과 Swagger UI에 그대로 표시됩니다.
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

    # 예제 쇼핑몰 API는 AI가 문서화할 OpenAPI 스펙의 재료가 됩니다.
    # 각 router 파일은 한 주제의 엔드포인트를 모아 두고, 여기서 앱에 연결합니다.
    app.include_router(health_router)
    app.include_router(products_router)
    app.include_router(orders_router)
    app.include_router(users_router)

    # /ai-docs 라우터는 현재 서버의 openapi.json을 읽어 문서를 생성합니다.
    app.include_router(documents_router)

    # Swagger UI의 Authorize 버튼 이름과 보안 스키마를 수업용으로 고정합니다.
    app.openapi = lambda: custom_openapi(app)
    return app


app = create_app()
