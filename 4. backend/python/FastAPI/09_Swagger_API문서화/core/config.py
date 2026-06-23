import os

from fastapi import FastAPI


tags_metadata = [
    {"name": "Products", "description": "상품 조회, 등록, 수정, 삭제"},
    {"name": "Orders", "description": "주문 생성 및 상태 관리"},
    {"name": "Users", "description": "회원 가입 및 정보 관리"},
    {"name": "Health", "description": "서버 상태 확인"},
]


def create_app() -> FastAPI:
    is_production = os.getenv("ENV", "development") == "production"

    return FastAPI(
        title="쇼핑몰 REST API",
        summary="상품·주문·회원 관리를 위한 REST API",
        description="""
## 개요

이 API는 쇼핑몰 백엔드 서비스의 핵심 기능을 제공합니다.

## 인증

보호된 엔드포인트는 `Authorization: Bearer <token>` 헤더가 필요합니다.
실습용 관리자 토큰은 `demo-admin-token`입니다.

## 에러 응답 형식

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "사람이 읽을 수 있는 설명"
    }
}
```

## 버전 정책

- **v1** (현재): 운영 중
""",
        version="1.0.0",
        contact={"name": "API 지원팀", "email": "api@example.com"},
        license_info={"name": "MIT"},
        openapi_tags=tags_metadata,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )
