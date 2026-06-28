from fastapi import FastAPI

from core.metadata import API_DESCRIPTION, API_VERSION, TAGS_METADATA, is_production
from core.openapi import custom_openapi
from routers.health import router as health_router
from routers.orders import router as orders_router
from routers.products import router as products_router
from routers.users import router as users_router


def create_app() -> FastAPI:
    docs_enabled = not is_production()
    app = FastAPI(
        title="쇼핑몰 REST API",
        summary="상품·주문·회원 관리를 위한 REST API",
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
    app.openapi = lambda: custom_openapi(app)
    return app


app = create_app()
