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
| `routers/documents.py` | 생성형 AI 문서 자동화 API |
| `services/document_workflow.py` | 문서 생성 흐름 조합 |
| `services/document_generator.py` | Groq에 전달할 프롬프트 작성 |
| `services/groq_client.py` | Groq 스트리밍 호출 |
| `services/openapi_spec.py` | OpenAPI 스펙 수집 및 compact 처리 |
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
| `PATCH` | `/products/{product_id}` | 상품 부분 수정 |
| `DELETE` | `/products/{product_id}` | 상품 삭제 |
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
  "server_url": "http://localhost:8000"
}
```

다른 FastAPI 서버를 문서화할 수도 있습니다.

```json
{
  "server_url": "http://localhost:9000/openapi.json"
}
```

---
## 실행 준비

```bash
uv sync
copy .env.example .env
```

`.env` 파일에 Groq API 키를 입력합니다.

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxx
```

---
## FastAPI 서버 실행

```bash
uv run python -m uvicorn main:app --reload --port 8000
```

브라우저에서 Swagger UI를 엽니다.

```text
http://localhost:8000/docs
```

---
## Swagger UI 실습 1: OpenAPI 확인

1. `GET /health`를 실행해 서버가 동작하는지 확인합니다.
2. `GET /products`를 실행해 예제 상품 목록을 확인합니다.
3. 브라우저에서 `http://localhost:8000/openapi.json`을 열어 JSON 스펙을 확인합니다.
4. `Products`, `Orders`, `Users`, `AI Documents` 태그가 보이는지 확인합니다.

---
## Swagger UI 실습 2: 인증 확인

1. Swagger UI 오른쪽 위 `Authorize` 버튼을 누릅니다.
2. 값에 `demo-admin-token`을 입력합니다.
3. `POST /products`를 실행합니다.
4. 토큰을 지운 뒤 다시 실행해 `401` 또는 `403` 응답을 확인합니다.

---
## Swagger UI 실습 3: API 문서 생성

`POST /ai-docs/api-docs`를 실행합니다.

요청 본문:

```json
{
  "server_url": "http://localhost:8000"
}
```

실행 후 다음 파일을 확인합니다.

```text
output/API_DOCS.md
```

---
## Swagger UI 실습 4: 전체 문서 생성

`POST /ai-docs/generate-all`을 실행합니다.

생성되는 파일:

| 파일 | 설명 |
|---|---|
| `output/API_DOCS.md` | 개발자용 API 문서 |
| `output/collection.json` | Postman Import용 Collection |
| `output/README.md` | GitHub README 초안 |
| `output/_spec_snapshot.json` | 변경 비교용 OpenAPI 스냅샷 |

---
## Swagger UI 실습 5: 변경 문서 생성

1. 먼저 `POST /ai-docs/generate-all`을 실행해 스냅샷을 저장합니다.
2. 라우터 코드의 설명이나 엔드포인트를 수정합니다.
3. 서버가 reload된 뒤 `POST /ai-docs/changes`를 실행합니다.
4. 변경이 있으면 `output/API_CHANGES.md`가 생성됩니다.

---
## 오류 상황 읽기

| 상황 | 원인 | 해결 |
|---|---|---|
| OpenAPI 스펙 연결 실패 | `server_url` 오류 또는 서버 미실행 | 서버 주소와 포트를 확인 |
| `401 인증이 필요합니다.` | Bearer 토큰 누락 | Swagger Authorize에 `demo-admin-token` 입력 |
| `403 관리자 권한이 필요합니다.` | 토큰 값 오류 | 토큰 문자열을 다시 확인 |
| Groq 요청 실패 | API 키 누락 또는 사용량 제한 | `.env`와 Groq 콘솔 확인 |
| 토큰 한도 초과 | OpenAPI 스펙 또는 출력이 너무 큼 | 스펙 compact 범위를 줄이거나 문서별 엔드포인트를 사용 |

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
