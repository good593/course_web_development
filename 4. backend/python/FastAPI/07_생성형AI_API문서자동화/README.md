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
# FastAPI로 만드는 생성형 AI API 문서 자동화

---
## 학습 목표

- FastAPI가 생성하는 `openapi.json`의 역할을 설명할 수 있다
- Swagger UI에 표시되는 설명, 예시, 인증 정보를 코드에서 작성할 수 있다
- FastAPI 엔드포인트 안에서 Groq API를 호출해 문서를 생성할 수 있다
- OpenAPI 스펙을 compact JSON으로 줄여 토큰 한도 문제를 줄일 수 있다
- API 문서, Postman Collection, README 초안을 HTTP API로 생성할 수 있다

---
## 이번 강의의 핵심

이번 강의는 별도 터미널 명령 도구를 만드는 수업이 아닙니다.

FastAPI 서버가 직접 다음 일을 처리합니다.

1. 자신의 `openapi.json` 또는 다른 FastAPI 서버의 `openapi.json`을 읽습니다.
2. OpenAPI 스펙에서 문서 생성에 필요한 정보만 추립니다.
3. Groq API에 프롬프트를 보냅니다.
4. 생성된 문서를 `output/` 폴더에 저장하고 HTTP 응답으로 돌려줍니다.

---
## 파일 구조

| 파일 | 역할 |
|---|---|
| `main.py` | FastAPI 앱 생성 및 라우터 등록 |
| `settings.py` | 모델, 출력 폴더, 기본 OpenAPI URL 설정 |
| `core/metadata.py` | Swagger 제목, 설명, 태그 메타데이터 |
| `core/security.py` | Swagger Authorize 버튼과 실습용 Bearer 토큰 |
| `core/openapi.py` | OpenAPI 보안 스키마 커스터마이징 |
| `schemas/*.py` | Swagger 요청/응답 본문과 예시 |
| `routers/documents.py` | 생성형 AI 문서 자동화 API |
| `services/document_workflow.py` | 문서 생성 흐름 조합 |
| `services/document_generator.py` | Groq에 전달할 프롬프트 작성 |
| `services/groq_client.py` | Groq 스트리밍 호출 |
| `services/openapi_spec.py` | OpenAPI 스펙 수집 및 compact 처리 |
| `services/storage.py` | 생성 결과와 스냅샷 파일 저장 |
| `routers/products.py` | 문서화 대상 예제 API |
| `routers/orders.py` | 문서화 대상 예제 API |
| `routers/users.py` | 문서화 대상 예제 API |

---
## FastAPI 앱 진입점

`main.py`가 강의의 기본 실행 파일입니다.

```python
def create_app() -> FastAPI:
    app = FastAPI(
        title="생성형 AI API 문서 자동화",
        summary="FastAPI OpenAPI 스펙을 Groq로 문서화하는 실습 API",
        description=API_DESCRIPTION,
        version=API_VERSION,
        openapi_tags=TAGS_METADATA,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.include_router(health_router)
    app.include_router(products_router)
    app.include_router(orders_router)
    app.include_router(users_router)
    app.include_router(documents_router)
    app.openapi = lambda: custom_openapi(app)
    return app
```

---
## 예제 API와 AI 문서화 API

하나의 FastAPI 서버 안에 두 종류의 엔드포인트가 있습니다.

| 구분 | 경로 | 역할 |
|---|---|---|
| 예제 API | `/products`, `/orders`, `/users` | 문서화 대상이 되는 쇼핑몰 API |
| AI 문서화 API | `/ai-docs/*` | OpenAPI 스펙을 Groq로 보내 문서 생성 |
| 상태 확인 | `/health` | 서버 상태 확인 |
| 자동 문서 | `/docs` | Swagger UI |
| 스펙 원본 | `/openapi.json` | OpenAPI JSON |

---
## 문서화 대상 엔드포인트

| 메서드 | 경로 | 기능 |
|---|---|---|
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/products` | 상품 목록 조회 |
| `POST` | `/products` | 상품 등록, 관리자 토큰 필요 |
| `GET` | `/products/{product_id}` | 상품 단건 조회 |
| `PATCH` | `/products/{product_id}` | 상품 부분 수정, 관리자 토큰 필요 |
| `DELETE` | `/products/{product_id}` | 상품 삭제, 관리자 토큰 필요 |
| `POST` | `/orders` | 주문 생성, 재고 차감 |
| `GET` | `/orders/{order_id}` | 주문 조회 |
| `POST` | `/users` | 회원 가입 |
| `GET` | `/users/me` | 내 정보 조회, 관리자 토큰 필요 |

---
## 생성형 AI 문서화 엔드포인트

| 메서드 | 경로 | 생성 결과 |
|---|---|---|
| `POST` | `/ai-docs/api-docs` | 개발자용 마크다운 API 문서 |
| `POST` | `/ai-docs/postman-collection` | Postman Collection JSON |
| `POST` | `/ai-docs/readme` | GitHub README 초안 |
| `POST` | `/ai-docs/generate-all` | 위 3개 문서 한 번에 생성 |
| `POST` | `/ai-docs/changes` | 변경된 엔드포인트만 문서화 |

---
## Swagger 문서에 들어가는 설명

FastAPI 라우터의 `summary`, `description`, `response_model`은 OpenAPI 스펙에 들어갑니다.

```python
@router.get(
    "",
    response_model=List[ProductResponse],
    summary="상품 목록 조회",
    description="등록된 상품을 카테고리 필터와 페이지네이션으로 조회합니다.",
    response_description="상품 목록",
)
def list_products(
    category: Optional[str] = Query(default=None, description="카테고리 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
) -> list[dict]:
```

---
## 요청 예시는 Pydantic 모델에 작성

`json_schema_extra`에 작성한 예시는 Swagger UI와 OpenAPI 스펙에 반영됩니다.

```python
class ProductCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "무선 마우스", "price": 35000, "stock": 50, "category": "전자제품"},
                {"name": "면 티셔츠", "price": 19900, "stock": 200, "category": "의류"},
            ]
        }
    )

    name: str = Field(min_length=2, max_length=100, description="상품명 (2~100자)")
    price: int = Field(gt=0, description="판매가 (원, 0 초과)")
    stock: int = Field(ge=0, default=0, description="재고 수량")
    category: str = Field(description="카테고리명")
```

---
## 인증 정보도 OpenAPI에 포함

보호된 엔드포인트는 `Authorization: Bearer demo-admin-token`을 사용합니다.

```python
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


def require_admin_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    if credentials.credentials != DEMO_ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return credentials.credentials
```

---
## OpenAPI 보안 스키마 커스터마이징

`core/openapi.py`는 Swagger UI의 Authorize 버튼에 사용할 보안 스키마를 추가합니다.

```python
schema["components"]["securitySchemes"] = {
    "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
}
```

---
## 전체 흐름

```text
FastAPI 요청
  POST /ai-docs/api-docs
        |
        v
GET /openapi.json
        |
        v
compact OpenAPI JSON
        |
        v
Groq API
        |
        v
output/API_DOCS.md 저장 + HTTP 응답 반환
```

---
## OpenAPI 스펙 수집

`server_url`에는 서버 기본 URL이나 `openapi.json` 전체 URL을 넣을 수 있습니다.

```python
def build_openapi_url(base_or_spec_url: str) -> str:
    url = base_or_spec_url.rstrip("/")
    if url.endswith("/openapi.json"):
        return url
    return f"{url}/openapi.json"


def fetch_openapi_spec(url: str = DEFAULT_OPENAPI_URL) -> dict:
    spec_url = build_openapi_url(url)
    response = httpx.get(spec_url, timeout=5)
    response.raise_for_status()
    return response.json()
```

---
## 프롬프트용 스펙 줄이기

OpenAPI JSON 전체를 그대로 보내면 토큰 한도를 넘기 쉽습니다.

```python
def format_spec_for_prompt(spec: dict) -> str:
    compact = compact_openapi_spec(spec)
    return json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
```

compact 단계에서는 다음 정보를 중심으로 남깁니다.

- API 제목, 설명, 버전
- 경로와 HTTP 메서드
- 파라미터와 요청 본문
- 응답 코드와 응답 스키마
- 보안 스키마

---
## Groq 호출

`services/groq_client.py`는 `.env`의 `GROQ_API_KEY`를 사용합니다.

```python
client = Groq()
stream = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    max_completion_tokens=max_tokens,
    reasoning_effort=reasoning_effort,
    reasoning_format="hidden",
    temperature=0.2,
    stream=True,
)
```

---
## 문서 생성 프롬프트

`services/document_generator.py`는 생성 목적별로 다른 프롬프트를 만듭니다.

| 함수 | 생성 결과 |
|---|---|
| `generate_api_docs()` | 개발자용 API 문서 |
| `generate_postman_collection()` | Postman Collection |
| `generate_readme()` | GitHub README |
| `generate_diff_docs()` | 변경 엔드포인트 문서 |

---
## FastAPI 라우터에서 호출

`routers/documents.py`는 HTTP 요청을 받아 서비스 함수를 호출합니다.

```python
@router.post(
    "/api-docs",
    response_model=GeneratedDocumentResponse,
    summary="API 문서 생성",
)
def generate_api_document(request: DocumentGenerationRequest) -> dict:
    try:
        return create_api_docs(request.server_url)
    except RuntimeError as error:
        raise_generation_error(error)
```

---
## 요청 본문

기본값은 현재 FastAPI 서버입니다.

```json
{
  "server_url": "http://localhost:8001"
}
```

다른 FastAPI 서버를 문서화할 수도 있습니다.

```json
{
  "server_url": "http://localhost:9000/openapi.json"
}
```

---
## 서버 실행 및 Swagger 실습

---
### 가상환경 생성

```bash
# pyproject.toml과 uv.lock 기준으로 의존성 설치
uv sync
```

AI 문서 생성 API까지 실행하려면 `.env` 파일에 Groq API 키를 넣습니다.

```powershell
Set-Content -Encoding UTF8 .env "GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxx"
```

> Groq API 키가 없어도 `GET /health`, `/products`, `/orders`, `/users` 실습은 먼저 진행할 수 있습니다.

---
### 서버 실행

```bash
python -m uvicorn main:app --reload --port 8001
```

---
### Swagger UI 실습 (http://localhost:8001/docs)
> 각 API에서 **Try it out**을 누른 뒤 아래 순서대로 입력합니다.

---
#### 실습 1. 서버 상태와 OpenAPI 원본 확인
> `GET /health`

확인할 것
- 응답 상태 코드가 `200 OK`입니다.
- 응답에 `status`, `version`, `timestamp`가 들어옵니다.
- 브라우저에서 `http://localhost:8001/openapi.json`을 열면 JSON 스펙이 보입니다.
- Swagger UI에 `Products`, `Orders`, `Users`, `AI Documents`, `Health` 태그가 보입니다.

---
#### 실습 2. 상품 목록 조회와 Query Parameter 확인
> `GET /products`

입력값:

| 이름 | 값 |
|---|---|
| `category` | `전자제품` |
| `page` | `1` |
| `size` | `10` |

확인할 것
- 응답 상태 코드가 `200 OK`입니다.
- 예제 상품인 `무선 마우스`, `기계식 키보드`가 조회됩니다.
- `category`, `page`, `size` 설명이 Swagger UI에 표시됩니다.

---
#### 실습 3. 인증 실패 응답 확인
> `POST /products`

아직 Authorize를 누르지 않은 상태에서 실행합니다.

```json
{
    "name": "USB-C 허브",
    "price": 42000,
    "stock": 30,
    "category": "전자제품"
}
```

확인할 것
- 응답 상태 코드가 `401 Unauthorized`입니다.
- 응답 본문은 `{"detail": "인증이 필요합니다."}` 형태입니다.

---
#### 실습 4. 관리자 토큰으로 상품 등록
> `POST /products`

1. Swagger UI 오른쪽 위 `Authorize` 버튼을 누릅니다.
2. 값에 `demo-admin-token`만 입력합니다.
3. 다시 `POST /products`를 실행합니다.

```json
{
    "name": "USB-C 허브",
    "price": 42000,
    "stock": 30,
    "category": "전자제품"
}
```

확인할 것
- 응답 상태 코드가 `201 Created`입니다.
- 응답에 새 상품 `id`가 들어옵니다.
- 같은 본문을 한 번 더 보내면 `409 Conflict`가 발생합니다.

---
#### 실습 5. 요청 검증 오류 확인
> `POST /products`

```json
{
    "name": "A",
    "price": 0,
    "stock": -1,
    "category": "전자제품"
}
```

확인할 것
- 응답 상태 코드가 `422 Unprocessable Entity`입니다.
- `name`, `price`, `stock` 필드 검증 오류가 `detail` 목록으로 표시됩니다.

---
#### 실습 6. 상품 수정과 삭제
> `PATCH /products/{product_id}`

`product_id`에는 실습 4에서 생성된 상품 ID를 넣습니다.

```json
{
    "price": 39900,
    "stock": 25
}
```

확인할 것
- 응답 상태 코드가 `200 OK`입니다.
- 전달한 필드만 변경됩니다.

삭제도 같은 상품 ID로 확인합니다.

> `DELETE /products/{product_id}`

확인할 것
- 응답 상태 코드가 `204 No Content`입니다.
- 같은 ID를 다시 조회하면 `404 Not Found`가 발생합니다.

---
#### 실습 7. 주문 생성과 재고 차감 확인
> `POST /orders`

```json
{
    "items": [
        {
            "product_id": 1,
            "quantity": 2
        }
    ]
}
```

확인할 것
- 응답 상태 코드가 `201 Created`입니다.
- 응답에 `id`, `items`, `total_price`, `status`, `created_at`이 들어옵니다.
- 다시 `GET /products/1`을 실행하면 재고가 줄어 있습니다.

---
#### 실습 8. 회원 가입과 내 정보 조회
> `POST /users`

```json
{
    "username": "hong123",
    "email": "hong@example.com",
    "password": "pass1234"
}
```

확인할 것
- 응답 상태 코드가 `201 Created`입니다.
- 응답에는 `password`가 포함되지 않습니다.
- 같은 이메일을 한 번 더 보내면 `409 Conflict`가 발생합니다.

이어서 관리자 토큰이 들어간 상태로 실행합니다.

> `GET /users/me`

확인할 것
- 응답 상태 코드가 `200 OK`입니다.
- 실습용 사용자 `demo_user`가 반환됩니다.

---
#### 실습 9. API 문서 생성
> `POST /ai-docs/api-docs`

```json
{
    "server_url": "http://localhost:8001"
}
```

확인할 것
- `.env`의 `GROQ_API_KEY`가 정상이라면 응답 상태 코드가 `200 OK`입니다.
- 응답에는 `endpoint_count`, `filename`, `path`, `content`가 들어옵니다.
- `output/API_DOCS.md` 파일이 생성됩니다.
- Groq API 키가 없거나 사용량 제한에 걸리면 `502 Bad Gateway`가 발생합니다.

---
#### 실습 10. Postman Collection과 README 생성
> `POST /ai-docs/generate-all`

```json
{
    "server_url": "http://localhost:8001/openapi.json"
}
```

생성되는 파일:

| 파일 | 설명 |
|---|---|
| `output/API_DOCS.md` | 개발자용 API 문서 |
| `output/collection.json` | Postman Import용 Collection |
| `output/README.md` | GitHub README 초안 |
| `output/_spec_snapshot.json` | 변경 비교용 OpenAPI 스냅샷 |

확인할 것
- 응답의 `files` 배열에 위 파일 경로가 들어옵니다.
- `server_url`은 서버 기본 URL과 `/openapi.json` 전체 URL을 모두 받을 수 있습니다.

---
#### 실습 11. 변경 문서 생성
> `POST /ai-docs/changes`

스냅샷 없이 먼저 실행해 봅니다.

```json
{
    "server_url": "http://localhost:8001"
}
```

확인할 것
- `generate-all`을 실행하기 전이면 `400 Bad Request`가 발생합니다.
- 응답 본문은 `{"detail": "이전 스냅샷이 없습니다. 먼저 /ai-docs/generate-all을 실행하세요."}` 형태입니다.

이후 `POST /ai-docs/generate-all`을 한 번 실행해 스냅샷을 저장합니다.

1. `routers/products.py`의 `summary`나 `description` 문구를 잠깐 수정합니다.
2. 서버가 reload된 뒤 `POST /ai-docs/changes`를 다시 실행합니다.
3. 변경이 있으면 `output/API_CHANGES.md`가 생성됩니다.

---
## 오류 상황 읽기

| 상태 코드 | 상황 | 확인할 것 |
|---|---|---|
| `400` | 변경 비교용 스냅샷 없음 | 먼저 `POST /ai-docs/generate-all` 실행 |
| `401` | Bearer 토큰 누락 | Swagger Authorize에 `demo-admin-token` 입력 |
| `403` | Bearer 토큰 값 오류 | `Bearer` 접두어 없이 토큰 문자열만 입력 |
| `404` | 존재하지 않는 상품/주문 ID | 경로 파라미터 ID 확인 |
| `409` | 상품명 또는 이메일 중복 | 다른 `name` 또는 `email` 사용 |
| `422` | 요청 본문/파라미터 검증 실패 | `Field`의 `min_length`, `gt`, `ge` 조건 확인 |
| `502` | OpenAPI 스펙 수집 또는 Groq 호출 실패 | 서버 주소, `.env`, Groq 사용량 제한 확인 |

---
## 핵심 정리

| 개념 | 이 실습의 구현 |
|---|---|
| FastAPI 앱 | `main.py` |
| Swagger/OpenAPI | `/docs`, `/openapi.json` |
| AI 문서 생성 API | `routers/documents.py` |
| OpenAPI 수집 | `services/openapi_spec.py` |
| 스펙 축소 | `compact_openapi_spec()` |
| Groq 호출 | `services/groq_client.py` |
| 결과 저장 | `services/storage.py` |
| 변경 감지 | `output/_spec_snapshot.json` |

---
## 오늘의 결론

FastAPI와 생성형 AI를 연결하면 API 문서화도 하나의 백엔드 기능으로 만들 수 있습니다.

중요한 것은 AI 호출 자체보다 좋은 OpenAPI 스펙을 만드는 일입니다.

라우터의 설명, Pydantic 스키마, 예시, 인증 정보가 잘 작성되어 있을수록
생성형 AI가 더 정확한 문서를 만들 수 있습니다.
