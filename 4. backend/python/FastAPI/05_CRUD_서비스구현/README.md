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
# SQLite 블로그 CRUD 서비스 구현

---
## 학습 목표

- 인메모리 저장소 대신 SQLite 파일 DB에 데이터를 저장한다.
- `CREATE`, `READ`, `UPDATE`, `DELETE` 흐름을 게시글 API로 구현한다.
- `APIRouter`, `schemas`, `models` 구조를 실제 DB 예제에 적용한다.
- Swagger UI에서 정상 응답, `404`, `409`, `422` 응답을 직접 확인한다.

---
## 핵심 요약

| 개념 | 설명 |
|------|------|
| `sqlite3` | Python 표준 라이브러리 SQLite 드라이버 |
| `blog.db` | 실행 시 자동 생성되는 SQLite 데이터베이스 파일 |
| `sqlite3.Row` | 조회 결과를 dict처럼 다룰 수 있게 해주는 row factory |
| `PRAGMA foreign_keys = ON` | SQLite에서 외래 키 동작을 활성화 |
| `exclude_unset=True` | PATCH 요청에서 보낸 필드만 수정 |
| `ON DELETE SET NULL` | 카테고리 삭제 시 게시글은 남기고 `category_id`만 비움 |

---
## 1. 이전 장과 연결

`04_프로젝트구조화`에서는 Todo API를 파일별로 나누었습니다.

```
main.py
routers/todo.py
schemas/todo.py
models/todo.py
```

이번 장에서는 같은 구조를 유지하되 저장소만 바꿉니다.

| 이전 장 | 이번 장 |
|--------|---------|
| 인메모리 dict | SQLite 파일 DB |
| Todo 데이터 | 블로그 카테고리, 게시글 |
| 서버 재시작 시 데이터 사라짐 | `blog.db`에 데이터 유지 |
| 단순 저장/조회 | CRUD + 검색 + 필터링 |

---
## 2. 프로젝트 구조

```
05_CRUD_서비스구현/
├── main.py
├── models/
│   └── blog.py
├── routers/
│   ├── categories.py
│   └── posts.py
├── schemas/
│   └── blog.py
├── pyproject.toml
└── requirements.txt
```

---
### 파일 역할

| 파일 | 역할 |
|------|------|
| `main.py` | FastAPI 앱 생성, DB 초기화, 라우터 등록 |
| `schemas/blog.py` | 카테고리/게시글 요청 및 응답 형식 |
| `models/blog.py` | SQLite 연결, 테이블 생성, CRUD 쿼리 |
| `routers/categories.py` | 카테고리 API |
| `routers/posts.py` | 게시글 API |

---
## 3. SQLite를 사용하는 이유

---
### 인메모리 저장소의 한계

```python
class TodoDB:
    def __init__(self):
        self._data: dict[int, dict] = {}
```

- 구현이 쉽습니다.
- 하지만 서버를 재시작하면 데이터가 모두 사라집니다.
- 여러 테이블의 관계를 연습하기 어렵습니다.

---
### SQLite로 바꾸면

```python
DB_PATH = Path(__file__).resolve().parents[1] / "blog.db"

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

- 별도 DB 서버 없이 파일 하나로 동작합니다.
- Python 표준 라이브러리라 추가 DB 패키지가 필요 없습니다.
- SQL과 테이블 관계를 가볍게 연습할 수 있습니다.

---
## 4. 테이블 설계

---
### categories

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | INTEGER | 기본 키 |
| `name` | TEXT | 카테고리 이름, 중복 불가 |
| `description` | TEXT | 카테고리 설명 |
| `created_at` | TEXT | 생성 시각 |

---
### posts

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | INTEGER | 기본 키 |
| `title` | TEXT | 게시글 제목 |
| `content` | TEXT | 게시글 본문 |
| `summary` | TEXT | 게시글 요약 |
| `published` | INTEGER | 공개 여부, `0` 또는 `1` |
| `category_id` | INTEGER | 카테고리 외래 키 |
| `created_at` | TEXT | 생성 시각 |
| `updated_at` | TEXT | 수정 시각 |

---
### 외래 키

```sql
FOREIGN KEY (category_id)
    REFERENCES categories(id)
    ON DELETE SET NULL
```

카테고리를 삭제해도 게시글 자체는 삭제하지 않습니다.

대신 게시글의 `category_id`가 `null`로 바뀝니다.

---
## 5. DB 초기화

`main.py`에서 앱이 만들어질 때 `init_db()`를 먼저 실행합니다.

```python
from fastapi import FastAPI

from models.blog import init_db
from routers.categories import router as category_router
from routers.posts import router as post_router

init_db()

app = FastAPI(title="SQLite Blog API")

app.include_router(category_router)
app.include_router(post_router)
```

---
### init_db()

```python
def init_db() -> None:
    with closing(_connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (...);
            CREATE TABLE IF NOT EXISTS posts (...);
            """
        )
        conn.commit()
```

`IF NOT EXISTS`를 사용하면 서버를 여러 번 실행해도 기존 테이블을 덮어쓰지 않습니다.

---
## 6. Pydantic 스키마

---
### 생성 스키마

```python
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: str | None = Field(default=None, max_length=500)
    published: bool = Field(default=False)
    category_id: int | None = Field(default=None)
```

클라이언트가 게시글을 만들 때 보내는 값만 정의합니다.

---
### 수정 스키마

```python
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    summary: str | None = Field(default=None, max_length=500)
    published: bool | None = None
    category_id: int | None = None
```

PATCH 요청에서는 모든 필드를 선택 사항으로 둡니다.

---
### 응답 스키마

```python
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    published: bool
    category_id: int | None
    created_at: datetime
    updated_at: datetime
```

서버가 만들어 주는 `id`, `created_at`, `updated_at`은 응답 스키마에 포함합니다.

---
## 7. SQLite CRUD 패턴

---
### CREATE

```python
cursor = conn.execute(
    """
    INSERT INTO posts (
        title, content, summary, published,
        category_id, created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (...),
)
conn.commit()
```

`?` 자리에 값을 따로 전달하면 SQL Injection 위험을 줄일 수 있습니다.

---
### READ

```python
row = conn.execute(
    "SELECT * FROM posts WHERE id = ?",
    (post_id,),
).fetchone()
```

`fetchone()`은 한 건을 가져오고, 결과가 없으면 `None`을 반환합니다.

---
### UPDATE

```python
payload = data.model_dump(exclude_unset=True)

for field in ("title", "content", "summary", "published", "category_id"):
    if field in payload:
        fields.append(f"{field} = ?")
        values.append(payload[field])
```

`exclude_unset=True`를 쓰면 요청 Body에 들어온 필드만 수정합니다.

---
### DELETE

```python
cursor = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
conn.commit()
return cursor.rowcount > 0
```

`rowcount`가 `0`이면 삭제할 대상이 없었다는 뜻입니다.

---
## 8. 게시글 목록 조회

```python
def list_posts(
    skip: int = 0,
    limit: int = 10,
    category_id: int | None = None,
    published_only: bool = False,
    search: str | None = None,
):
    ...
```

---
### Query Parameter

| 파라미터 | 의미 |
|----------|------|
| `skip` | 앞에서 건너뛸 게시글 수 |
| `limit` | 가져올 게시글 수 |
| `category_id` | 특정 카테고리 게시글만 조회 |
| `published_only` | 공개 게시글만 조회 |
| `search` | 제목 또는 본문 키워드 검색 |

---
### 목록 응답

```json
{
  "total": 3,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "title": "FastAPI와 SQLite로 CRUD 만들기",
      "published": false,
      "category_id": 1
    }
  ]
}
```

목록 API는 실제 게시글 배열뿐 아니라 전체 개수와 페이지 정보도 함께 반환합니다.

---
## 9. 라우터 구현

---
### 카테고리 라우터

```python
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.post("", response_model=schemas.CategoryResponse, status_code=201)
def create_category(category: schemas.CategoryCreate):
    if blog_db.get_category_by_name(category.name):
        raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
    return blog_db.create_category(category)
```

중복 이름은 `409 Conflict`로 응답합니다.

---
### 게시글 라우터

```python
@router.post("", response_model=schemas.PostResponse, status_code=201)
def create_post(post: schemas.PostCreate):
    _validate_category(post.category_id)
    return blog_db.create_post(post)
```

존재하지 않는 카테고리 ID로 게시글을 만들면 `400 Bad Request`로 응답합니다.

---
### 게시글 부분 수정

```python
@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: int, post: schemas.PostUpdate):
    if not blog_db.get_post(post_id):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    if "category_id" in post.model_fields_set:
        _validate_category(post.category_id)

    return blog_db.update_post(post_id, post)
```

`category_id`를 아예 보내지 않는 것과 `null`로 보내는 것은 다릅니다.

---
## 10. 실행

### 의존성 설치

```bash
uv sync
```

또는

```bash
pip install -r requirements.txt
```

---
### 서버 실행

```bash
python -m uvicorn main:app --reload --port 8001
```

Swagger UI:

```text
http://localhost:8001/docs
```

서버를 실행하면 같은 폴더에 `blog.db` 파일이 자동으로 생성됩니다.

---
## 11. Swagger UI 실습

각 API에서 **Try it out**을 누른 뒤 아래 순서대로 실행합니다.

---
### 실습 1. 루트 엔드포인트 확인

> `GET /`

확인할 것

- `docs` 값이 `/docs`로 안내됩니다.
- `database` 값이 `blog.db`입니다.
- `categories`, `posts` 라우터가 `main.py`에 연결되어 있습니다.

---
### 실습 2. 비어 있는 목록 조회

> `GET /categories`

응답 예시:

```json
[]
```

---
> `GET /posts`

응답 예시:

```json
{
  "total": 0,
  "skip": 0,
  "limit": 10,
  "items": []
}
```

---
### 실습 3. 카테고리 생성

> `POST /categories`

```json
{
  "name": "기술",
  "description": "FastAPI, Python, 데이터베이스 관련 글"
}
```

확인할 것

- 응답 상태 코드가 `201 Created`입니다.
- 요청에는 없던 `id`, `created_at`이 응답에 포함됩니다.

---
### 실습 4. 중복 카테고리 확인

> `POST /categories`

같은 Body를 한 번 더 실행합니다.

확인할 것

- 응답 상태 코드가 `409 Conflict`입니다.
- `detail` 값이 `"이미 존재하는 카테고리 이름입니다"`입니다.

---
### 실습 5. 게시글 생성

> `POST /posts`

```json
{
  "title": "FastAPI와 SQLite로 CRUD 만들기",
  "content": "sqlite3 표준 라이브러리로 게시글을 저장합니다.",
  "summary": "SQLite 기반 CRUD 실습",
  "category_id": 1
}
```

확인할 것

- 응답 상태 코드가 `201 Created`입니다.
- `published`는 요청에서 생략했으므로 `false`입니다.
- `category_id`는 `1`입니다.

---
### 실습 6. 게시글 목록과 상세 조회

> `GET /posts`

확인할 것

- `total`이 `1`입니다.
- `items` 배열에 방금 만든 게시글이 들어 있습니다.

---
> `GET /posts/{post_id}`

| Path Parameter | 입력값 |
|----------------|--------|
| `post_id` | `1` |

확인할 것

- 응답 상태 코드가 `200 OK`입니다.
- 응답 구조는 `PostResponse`와 같습니다.

---
### 실습 7. 게시글 공개

> `POST /posts/{post_id}/publish`

| Path Parameter | 입력값 |
|----------------|--------|
| `post_id` | `1` |

확인할 것

- `published`가 `true`로 바뀝니다.
- `updated_at` 값이 갱신됩니다.

---
### 실습 8. 공개 게시글만 조회

> `GET /posts`

| Query Parameter | 입력값 |
|-----------------|--------|
| `published_only` | `true` |

확인할 것

- 공개된 게시글만 `items`에 들어옵니다.

---
### 실습 9. 키워드 검색

> `GET /posts`

| Query Parameter | 입력값 |
|-----------------|--------|
| `search` | `SQLite` |

확인할 것

- 제목 또는 본문에 `SQLite`가 들어간 게시글만 조회됩니다.

---
### 실습 10. 게시글 부분 수정

> `PATCH /posts/{post_id}`

| Path Parameter | 입력값 |
|----------------|--------|
| `post_id` | `1` |

```json
{
  "summary": "PATCH로 요약만 수정했습니다."
}
```

확인할 것

- `summary`만 바뀝니다.
- `title`, `content`, `published`, `category_id`는 유지됩니다.
- 이 동작은 `exclude_unset=True` 때문에 가능합니다.

---
### 실습 11. 카테고리 연결 해제

> `PATCH /posts/{post_id}`

```json
{
  "category_id": null
}
```

확인할 것

- `category_id`가 `null`로 바뀝니다.
- 필드를 생략한 것이 아니라 명시적으로 `null`을 보냈기 때문에 값이 비워집니다.

---
### 실습 12. 존재하지 않는 게시글 조회

> `GET /posts/{post_id}`

| Path Parameter | 입력값 |
|----------------|--------|
| `post_id` | `999` |

확인할 것

- 응답 상태 코드가 `404 Not Found`입니다.
- `detail` 값이 `"게시글을 찾을 수 없습니다"`입니다.

---
### 실습 13. Body 검증 실패 확인

> `POST /posts`

```json
{
  "title": "",
  "content": ""
}
```

확인할 것

- 응답 상태 코드가 `422 Unprocessable Entity`입니다.
- `title`, `content`가 `min_length=1` 검증을 통과하지 못합니다.

---
### 실습 14. 게시글 삭제

> `DELETE /posts/{post_id}`

| Path Parameter | 입력값 |
|----------------|--------|
| `post_id` | `1` |

확인할 것

- 응답 상태 코드가 `204 No Content`입니다.
- 다시 `GET /posts/1`을 실행하면 `404 Not Found`입니다.

---
## 12. 추가 실습

---
### 카테고리 삭제와 외래 키

1. 카테고리를 하나 더 만듭니다.
2. 그 카테고리 ID로 게시글을 만듭니다.
3. `DELETE /categories/{category_id}`를 실행합니다.
4. 게시글 상세를 다시 조회합니다.

확인할 것

- 게시글은 삭제되지 않습니다.
- `category_id`만 `null`로 바뀝니다.
- 이 동작은 `ON DELETE SET NULL`로 정의했습니다.

---
### 존재하지 않는 카테고리로 게시글 생성

> `POST /posts`

```json
{
  "title": "잘못된 카테고리 테스트",
  "content": "존재하지 않는 카테고리 ID를 사용합니다.",
  "category_id": 999
}
```

확인할 것

- 응답 상태 코드가 `400 Bad Request`입니다.
- `detail` 값이 `"존재하지 않는 카테고리입니다"`입니다.

---
## 핵심 패턴 정리

| 상황 | 코드 패턴 |
|------|-----------|
| DB 연결 | `sqlite3.connect(DB_PATH)` |
| dict 형태 조회 | `conn.row_factory = sqlite3.Row` |
| 외래 키 활성화 | `PRAGMA foreign_keys = ON` |
| 단건 없음 | `if not post: raise HTTPException(404, ...)` |
| 중복 리소스 | `raise HTTPException(409, ...)` |
| 부분 수정 | `model_dump(exclude_unset=True)` |
| 공개 필터 | `published_only=true` |
| 페이지네이션 | `LIMIT ? OFFSET ?` |

---
## 다음 장으로 연결

이번 장에서는 SQLite와 SQL을 직접 다루었습니다.

다음 단계에서는 같은 블로그 API를 더 큰 서비스에 맞게 나눕니다.

- Repository: DB 쿼리 담당
- Service: 비즈니스 규칙 담당
- Router: HTTP 요청/응답 담당
- SQLAlchemy: SQL을 Python 객체 모델로 다루는 ORM

