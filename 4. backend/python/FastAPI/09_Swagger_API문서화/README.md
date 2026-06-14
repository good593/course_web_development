---
style: |
  img {
    display: block;
    float: none;
    margin-left: auto;
    margin-right: auto;
  }
marp: true
paginate: true
---
# Swagger 기반 API 문서화

---
## 학습 목표

- FastAPI가 OpenAPI 스펙을 자동으로 생성하는 원리를 이해한다
- 엔드포인트·파라미터·응답에 문서 메타데이터를 추가할 수 있다
- 다양한 응답 코드를 Swagger UI에 표현할 수 있다
- 실무 수준의 API 문서를 자동화할 수 있다

---
## [Swagger란?](https://swagger.io/)
> Swagger는 REST API를 설계하고, 문서화하고, 테스트할 수 있도록 도와주는 도구 및 명세(OpenAPI Specification 기반)입니다.

| 항목 | 설명 |
|---|---|
| Swagger | REST API를 문서화하고 테스트할 수 있는 도구 모음 |
| OpenAPI | API를 기술하는 표준 명세(Specification) |
| 주요 기능 | API 문서 자동 생성, 요청/응답 명세 제공, 브라우저 기반 테스트 |
| 장점 | 협업 효율 향상, 문서 최신화 자동화, 개발 및 테스트 편의성 증가 |
| 단점 | 운영 환경 노출 주의 필요, 문서 품질은 개발자의 작성 수준에 의존 |
| FastAPI | `/docs`(Swagger UI), `/redoc` 문서를 자동 제공 |

---
## 1. FastAPI의 자동 문서화 원리

FastAPI는 코드를 분석해 **OpenAPI 3.x 스펙(JSON)**을 자동으로 생성합니다.  
이 JSON을 두 가지 UI로 렌더링합니다.

| URL | UI | 특징 |
|-----|-----|------|
| `/docs` | Swagger UI | 브라우저에서 직접 API 호출 가능 |
| `/redoc` | ReDoc | 가독성 높은 읽기 전용 문서 |
| `/openapi.json` | 원본 스펙 | Postman 등 외부 도구에서 가져오기 가능 |

---
## 2. 앱 수준 메타데이터

```python
from fastapi import FastAPI

app = FastAPI(
    title="쇼핑몰 API",
    summary="상품·주문·회원 관리를 위한 REST API",
    description="""
이 API는 쇼핑몰 백엔드 서비스를 제공합니다.
""",
    version="1.0.0",
    contact={
        "name": "API 지원팀",
        "email": "api-support@example.com",
    },
    docs_url="/docs",       # Swagger UI 경로 (None으로 비활성화 가능)
    redoc_url="/redoc",     # ReDoc 경로
    openapi_url="/openapi.json",
)
```

---
## 3. 태그(Tags) — 엔드포인트 그룹화

```python
from fastapi import FastAPI

# 태그 메타데이터 정의
tags_metadata = [
    {
        "name": "Products",
        "description": "상품 조회, 등록, 수정, 삭제",
    },
    {
        "name": "Orders",
        "description": "주문 생성 및 상태 관리",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/products", tags=["Products"])
def list_products(): ...

@app.post("/orders", tags=["Orders"])
def create_order(): ...
```

---
## 4. 엔드포인트 문서화

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get(
    "/products/{product_id}",
    tags=["Products"],
    summary="상품 단건 조회",
    description="ID로 특정 상품의 상세 정보를 조회합니다. 비활성 상품은 404를 반환합니다.",
    response_description="조회된 상품 정보",
    deprecated=False,           # True로 설정하면 취소선 표시
)
def get_product(
    product_id: int = Path(
        description="조회할 상품의 고유 ID",
        ge=1,
        examples={"기본 예시": {"value": 1}},
    ),
    include_reviews: bool = Query(
        default=False,
        description="True이면 리뷰 목록도 함께 반환",
    ),
):
    ...
```

---
## 5. 다양한 응답 코드 문서화

`responses` 파라미터로 각 HTTP 상태 코드를 Swagger UI에 표현합니다.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ProductResponse(BaseModel):
    name: str
    price: int

@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,         # 200 응답 모델
    ...
)
def get_product(product_id: int):
    ...
```

---
## 6. 요청 본문 예시(examples) 추가

Pydantic `Field(examples=...)`와 `model_config`를 활용합니다.

```python
from pydantic import BaseModel, Field, ConfigDict

class ProductCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "무선 마우스",
                    "price": 35000,
                }
            ]
        }
    )

    name: str = Field(description="상품명", min_length=2, max_length=100)
    price: int = Field(description="판매가 (원)", gt=0)
```

---
## 7. 보안 스키마 문서화
> Swagger UI에서 우측 상단 **Authorize** 버튼이 자동으로 생성됩니다.

```python
app = FastAPI()
bearer_scheme = HTTPBearer(auto_error=False)

def require_admin_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    return credentials.credentials

@app.get()
def get_me(token: str = Security(require_admin_token)):
    ...
```

---
## 8. OpenAPI 스펙 커스터마이징

```python
app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 전역 보안 스키마 추가
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
```

---
## 9. Swagger UI 비활성화 (운영 환경)

```python
import os
from fastapi import FastAPI

# 운영 환경에서는 문서 비노출
is_production = os.getenv("ENV", "development") == "production"

app = FastAPI(
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)
```

---
## 핵심 정리

| 기능 | 방법 |
|------|------|
| 앱 제목·설명 | `FastAPI(title=, description=, version=)` |
| 엔드포인트 그룹 | `tags=["그룹명"]` + `openapi_tags=` |
| 엔드포인트 설명 | `summary=`, `description=`, `response_description=` |
| 응답 코드 문서화 | `responses={404: {...}, 409: {...}}` |
| 요청 예시 | `model_config = ConfigDict(json_schema_extra={"examples": [...]})` |
| 파라미터 설명 | `Path(description=)`, `Query(description=)`, `Field(description=)` |
| 인증 버튼 | `HTTPBearer()` + `Security(...)` |
