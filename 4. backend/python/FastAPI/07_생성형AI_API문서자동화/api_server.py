import os
from fastapi import FastAPI, Path, Query, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime

# ── 앱 수준 메타데이터 ────────────────────────────────────────────────────────

tags_metadata = [
    {"name": "Products", "description": "상품 조회, 등록, 수정, 삭제"},
    {"name": "Orders",   "description": "주문 생성 및 상태 관리"},
    {"name": "Users",    "description": "회원 가입 및 정보 관리"},
    {"name": "Health",   "description": "서버 상태 확인"},
]

is_production = os.getenv("ENV", "development") == "production"

app = FastAPI(
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

bearer_scheme = HTTPBearer(auto_error=False)

# ── 공통 스키마 ───────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict

COMMON_ERRORS = {
    401: {"description": "인증 토큰 없음 또는 만료", "model": ErrorResponse},
    403: {"description": "권한 없음", "model": ErrorResponse},
    422: {"description": "요청 데이터 형식 오류"},
    500: {"description": "서버 내부 오류"},
}

DEMO_ADMIN_TOKEN = "demo-admin-token"


def require_admin_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    if credentials.credentials != DEMO_ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return credentials.credentials

# ── 상품 스키마 ───────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "무선 마우스", "price": 35000, "stock": 50, "category": "전자제품"},
                {"name": "면 티셔츠",   "price": 19900, "stock": 200, "category": "의류"},
            ]
        }
    )

    name: str = Field(min_length=2, max_length=100, description="상품명 (2~100자)")
    price: int = Field(gt=0, description="판매가 (원, 0 초과)")
    stock: int = Field(ge=0, default=0, description="재고 수량")
    category: str = Field(description="카테고리명")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="변경할 상품명")
    price: Optional[int] = Field(default=None, gt=0, description="변경할 판매가")
    stock: Optional[int] = Field(default=None, ge=0, description="변경할 재고 수량")


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    category: str
    created_at: datetime


# ── 주문 스키마 ───────────────────────────────────────────────────────────────

class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0, description="주문할 상품 ID")
    quantity: int = Field(gt=0, description="주문 수량")

class OrderCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"items": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]}
            ]
        }
    )
    items: List[OrderItemIn] = Field(min_length=1, description="주문 상품 목록")


class OrderResponse(BaseModel):
    id: int
    items: List[dict]
    total_price: int
    status: str
    created_at: datetime


# ── 회원 스키마 ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"username": "hong123", "email": "hong@example.com", "password": "pass1234"}]
        }
    )
    username: str = Field(min_length=3, max_length=30, description="사용자명 (3~30자)")
    email: str = Field(description="이메일 주소")
    password: str = Field(min_length=8, description="비밀번호 (8자 이상)")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


# ── 인메모리 DB ───────────────────────────────────────────────────────────────

products_db: dict[int, dict] = {
    1: {"id": 1, "name": "무선 마우스", "price": 35000, "stock": 50, "category": "전자제품", "created_at": datetime(2024, 1, 10)},
    2: {"id": 2, "name": "기계식 키보드", "price": 89000, "stock": 20, "category": "전자제품", "created_at": datetime(2024, 1, 15)},
}
orders_db: dict[int, dict] = {}
users_db: dict[int, dict] = {}
_next_ids = {"product": 3, "order": 1, "user": 1}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    tags=["Health"],
    summary="서버 상태 확인",
    response_description="서버 상태 정보",
)
def health_check():
    return {"status": "ok", "version": app.version, "timestamp": datetime.now().isoformat()}


# ── 상품 엔드포인트 ───────────────────────────────────────────────────────────

@app.get(
    "/products",
    response_model=List[ProductResponse],
    tags=["Products"],
    summary="상품 목록 조회",
    description="등록된 상품을 카테고리 필터와 페이지네이션으로 조회합니다.",
    response_description="상품 목록",
)
def list_products(
    category: Optional[str] = Query(default=None, description="카테고리 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
):
    items = list(products_db.values())
    if category:
        items = [p for p in items if p["category"] == category]
    start = (page - 1) * size
    return items[start: start + size]


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=201,
    tags=["Products"],
    summary="상품 등록",
    description="새 상품을 등록합니다. 관리자 권한이 필요합니다.",
    response_description="등록된 상품 정보",
    responses={
        409: {"description": "동일한 상품명이 이미 존재함", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_product(
    product: ProductCreate,
    token: str = Security(require_admin_token),
):
    if any(p["name"] == product.name for p in products_db.values()):
        raise HTTPException(status_code=409, detail="동일한 상품명이 이미 존재합니다.")

    pid = _next_ids["product"]
    _next_ids["product"] += 1
    new_product = {"id": pid, **product.model_dump(), "created_at": datetime.now()}
    products_db[pid] = new_product
    return new_product


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="상품 단건 조회",
    description="ID로 특정 상품의 상세 정보를 조회합니다.",
    response_description="조회된 상품 정보",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def get_product(
    product_id: int = Path(description="조회할 상품 ID", ge=1, examples={"기본 예시": {"value": 1}}),
):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


@app.patch(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="상품 부분 수정",
    description="상품 정보를 부분적으로 수정합니다. 전달된 필드만 업데이트됩니다.",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def update_product(product_id: int, update: ProductUpdate):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    product.update(update.model_dump(exclude_none=True))
    return product


@app.delete(
    "/products/{product_id}",
    status_code=204,
    tags=["Products"],
    summary="상품 삭제",
    description="상품을 삭제합니다. 삭제된 상품은 복구할 수 없습니다.",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    del products_db[product_id]


# ── 주문 엔드포인트 ───────────────────────────────────────────────────────────

@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=201,
    tags=["Orders"],
    summary="주문 생성",
    description="상품을 주문합니다. 재고 확인 후 자동으로 재고가 차감됩니다.",
    responses={
        400: {"description": "재고 부족", "model": ErrorResponse},
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_order(order: OrderCreate):
    items_detail = []
    total = 0

    for item in order.items:
        product = products_db.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"상품 ID {item.product_id}를 찾을 수 없습니다.")
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail={"code": "INSUFFICIENT_STOCK", "product_id": item.product_id,
                        "available": product["stock"], "requested": item.quantity},
            )
        total += product["price"] * item.quantity
        items_detail.append({"product_id": item.product_id, "name": product["name"],
                              "quantity": item.quantity, "unit_price": product["price"]})

    for item in order.items:
        products_db[item.product_id]["stock"] -= item.quantity

    oid = _next_ids["order"]
    _next_ids["order"] += 1
    new_order = {"id": oid, "items": items_detail, "total_price": total,
                 "status": "pending", "created_at": datetime.now()}
    orders_db[oid] = new_order
    return new_order


@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="주문 조회",
    responses={404: {"description": "주문을 찾을 수 없음", "model": ErrorResponse}},
)
def get_order(order_id: int = Path(description="조회할 주문 ID", ge=1)):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    return order


# ── 회원 엔드포인트 ───────────────────────────────────────────────────────────

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    tags=["Users"],
    summary="회원 가입",
    responses={
        409: {"description": "이메일 또는 사용자명 중복", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_user(user: UserCreate):
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    uid = _next_ids["user"]
    _next_ids["user"] += 1
    new_user = {"id": uid, "username": user.username, "email": user.email, "created_at": datetime.now()}
    users_db[uid] = new_user
    return new_user


@app.get(
    "/users/me",
    response_model=UserResponse,
    tags=["Users"],
    summary="내 정보 조회",
    description="Bearer 토큰으로 인증 후 현재 사용자 정보를 반환합니다.",
    responses={
        401: {"description": "인증 토큰 없음 또는 만료", "model": ErrorResponse},
    },
)
def get_me(token: str = Security(require_admin_token)):
    # 실제 구현에서는 JWT 검증 후 토큰의 사용자 정보를 사용합니다.
    return {"id": 1, "username": "demo_user", "email": "demo@example.com", "created_at": datetime.now()}


# ── OpenAPI 커스터마이징 ──────────────────────────────────────────────────────

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
