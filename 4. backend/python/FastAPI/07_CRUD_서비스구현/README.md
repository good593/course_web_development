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
# CRUD 기반 백엔드 서비스 구현

---
## 학습 목표

- SQLAlchemy ORM으로 실제 DB와 연동하는 CRUD API 완성
- 페이지네이션, 키워드 검색, 필터링 쿼리 구현
- cascade 삭제와 DB 트랜잭션 처리
- 비즈니스 로직 검증 (공개 게시글에만 댓글, 게시글 있는 카테고리 삭제 방지)

---
## 1. 프로젝트 구조

```
13_CRUD_서비스구현/
├── main.py                  ← FastAPI 앱 생성 + 라우터 등록
├── core/
│   ├── database.py          ← DB 연결, 세션, Base
│   └── dependencies.py      ← Service 의존성 주입 함수
├── models/
│   └── blog.py              ← SQLAlchemy ORM 모델
├── schemas/
│   └── blog.py              ← Pydantic 입출력 스키마
├── repositories/
│   └── blog.py              ← DB 쿼리
├── services/
│   └── blog.py              ← 비즈니스 로직
└── routers/
    ├── categories.py        ← 카테고리 엔드포인트
    ├── posts.py             ← 게시글 엔드포인트
    └── comments.py          ← 댓글 엔드포인트
```

---
### 파일 역할 분담

| 파일 | 담당 |
|------|------|
| `core/database.py` | DB URL, engine, SessionLocal, `get_db()` |
| `models/blog.py` | 테이블 정의 (Column, ForeignKey, relationship) |
| `schemas/blog.py` | 입력/출력 형식 (Pydantic BaseModel) |
| `repositories/blog.py` | SQLAlchemy 쿼리와 DB commit/refresh |
| `services/blog.py` | 비즈니스 규칙 검증과 Repository 조합 |
| `core/dependencies.py` | 요청마다 DB 세션을 주입받아 Service 생성 |
| `routers/*.py` | URL별 엔드포인트 함수 |
| `main.py` | FastAPI 앱 생성, 테이블 생성, 라우터 등록 |

---
## 2. core/database.py — DB 연결

```python
DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db        # FastAPI 요청 처리 중 세션 유지
    finally:
        db.close()      # 요청 완료 후 세션 반환
```

**실습 포인트**: `main.py` 상단에서 앱 시작 전에 `Base.metadata.create_all(bind=engine)`를 호출해야 테이블이 자동 생성됩니다.

---
## 3. models/blog.py — SQLAlchemy 모델

---
### Category → Post → Comment 관계

```
Category
  id, name, description
  posts = relationship("Post", ...)        ← 역참조

Post
  id, title, content, summary, published
  category_id = ForeignKey("categories.id")
  category = relationship("Category", ...)  ← 부모 참조
  comments = relationship("Comment", cascade="all, delete-orphan")

Comment
  id, content, author
  post_id = ForeignKey("posts.id")
  post = relationship("Post", ...)
```

---
### cascade="all, delete-orphan"

```python
# Post 삭제 시 Comment도 자동 삭제
class Post(Base):
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",  # ← 이 설정이 없으면 FK 오류 발생
    )
```

```python
db.delete(post)   # Comment들도 함께 DELETE
db.commit()
```

---
## 4. schemas/blog.py — Pydantic 스키마

---
### 중첩 응답 — PostDetailResponse

게시글 단건 조회 시 카테고리 정보와 댓글 목록까지 함께 반환합니다.

```python
class PostDetailResponse(PostResponse):
    category: CategoryResponse | None = None    # 연관 카테고리 포함
    comments: list[CommentResponse] = []        # 댓글 리스트 포함
```

---
### 페이지네이션 응답 — PaginatedPosts

목록 API는 전체 수와 페이지 정보를 함께 반환해야 클라이언트가 페이지 네비게이션을 구현할 수 있습니다.

```python
class PaginatedPosts(BaseModel):
    total: int                      # 필터 조건에 맞는 전체 항목 수
    skip: int                       # 현재 오프셋
    limit: int                      # 페이지 크기
    items: list[PostResponse]       # 현재 페이지 데이터
```

---
### 스키마 목적별 규칙 복습

| 스키마 | 특징 |
|--------|------|
| `XxxCreate` | 필수 필드는 `...`, 클라이언트가 제공하는 값만 |
| `XxxUpdate` | 모든 필드 `None` 가능, `exclude_unset=True` 사용 |
| `XxxResponse` | `id`, 타임스탬프 포함, `from_attributes=True` |
| `XxxDetailResponse` | Response 상속 + 연관 모델 포함 |
| `Paginated...` | `total`, `skip`, `limit` + `items` 배열 |

---
## 5. repositories/blog.py — DB 쿼리

---
### 기본 CRUD 패턴

```python
from sqlalchemy.orm import Session

import models
import schemas


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    # 단건 조회
    def get_by_id(self, post_id: int) -> models.Post | None:
        return self.db.query(models.Post).filter(models.Post.id == post_id).first()

    # 생성
    def create(self, data: schemas.PostCreate) -> models.Post:
        post = models.Post(**data.model_dump())
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)   # ← DB에서 id, created_at 다시 읽기
        return post

    # 수정
    def update(self, post: models.Post, data: schemas.PostUpdate) -> models.Post:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(post, field, value)
        self.db.commit()
        self.db.refresh(post)
        return post

    # 삭제
    def delete(self, post: models.Post) -> None:
        self.db.delete(post)
        self.db.commit()
```

---
### 목록 조회 — 필터, 검색, 페이징

```python
def get_list(
    self,
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    published_only: bool = False,
    search: str | None = None,
) -> list[models.Post]:
    q = self.db.query(models.Post)

    if category_id:
        q = q.filter(models.Post.category_id == category_id)  # 카테고리 필터

    if published_only:
        q = q.filter(models.Post.published == True)            # 공개 게시글만

    if search:
        q = q.filter(models.Post.title.contains(search))      # 제목 키워드 검색

    return (
        q.order_by(models.Post.created_at.desc())  # 최신순 정렬
        .offset(skip)                               # 오프셋 (페이징)
        .limit(limit)                               # 최대 반환 수
        .all()
    )
```

---
### 전체 수 조회 (페이지네이션용)

```python
def count(self, category_id=None, published_only=False, search=None) -> int:
    q = self.db.query(models.Post)
    # 동일한 필터 조건 적용 ...
    return q.count()   # SELECT COUNT(*) ...
```

---
## 6. services/blog.py — 비즈니스 로직

---
### 검증 패턴

```python
from fastapi import HTTPException

import models
import schemas
from repositories import CategoryRepository, CommentRepository, PostRepository


class PostService:
    def _get_or_404(self, post_id: int) -> models.Post:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise HTTPException(404, "게시글을 찾을 수 없습니다")
        return post

    def publish_post(self, post_id: int) -> models.Post:
        post = self._get_or_404(post_id)

        # 비즈니스 규칙 검증
        if not post.content:
            raise HTTPException(400, "내용이 없는 게시글은 공개할 수 없습니다")
        if post.published:
            raise HTTPException(400, "이미 공개된 게시글입니다")

        return self.repo.update(post, schemas.PostUpdate(published=True))

    def add_comment(self, post_id: int, data: schemas.CommentCreate) -> models.Comment:
        post = self._get_or_404(post_id)
        if not post.published:
            raise HTTPException(400, "공개된 게시글에만 댓글을 달 수 있습니다")
        return self.comment_repo.create(post_id, data)
```

---
### 관계 삭제 방지

```python
def delete_category(self, cat_id: int) -> None:
    cat = self.repo.get_by_id(cat_id)
    if not cat:
        raise HTTPException(404, "카테고리를 찾을 수 없습니다")

    post_count = self.repo.count_posts(cat_id)
    if post_count > 0:
        raise HTTPException(
            400,
            f"게시글 {post_count}개가 속한 카테고리는 삭제할 수 없습니다",
        )
    self.repo.delete(cat)
```

---
## 7. core/dependencies.py — 의존성 주입

라우터 함수가 DB 세션을 직접 만들지 않도록, Service 생성 로직을 별도 파일로 분리합니다.

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services import CategoryService, PostService


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)
```

---
## 8. routers/posts.py — 엔드포인트와 Query 파라미터

```python
from core.dependencies import get_post_service
from services import PostService


@app.get("/posts", response_model=schemas.PaginatedPosts)
def list_posts(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 항목 수"),
    category_id: int | None = Query(None, description="카테고리 필터"),
    published_only: bool = Query(False, description="공개 게시글만"),
    search: str | None = Query(None, description="제목 키워드 검색"),
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(...)
```

`main.py`는 엔드포인트를 직접 들고 있지 않고, 각 라우터를 앱에 연결하는 역할만 담당합니다.

```python
app.include_router(category_router)
app.include_router(post_router)
app.include_router(comment_router)
```

---
### 요청 예시

```bash
# 전체 목록
GET /posts

# 기술 카테고리(id=1)의 공개 게시글, 2페이지 (20개씩)
GET /posts?category_id=1&published_only=true&skip=20&limit=20

# "FastAPI" 키워드 검색
GET /posts?search=FastAPI
```

---
### 응답 예시

```json
{
  "total": 42,
  "skip": 20,
  "limit": 20,
  "items": [
    {
      "id": 3,
      "title": "FastAPI 시작하기",
      "published": true,
      "created_at": "2025-01-15T09:30:00"
    }
  ]
}
```

---
## 9. 실행 및 테스트

### 서버 실행

```bash
uvicorn main:app --reload --port 8001
```

---
### 실습 순서

1. `POST /categories` — 카테고리 생성
2. `POST /posts` — 게시글 생성
3. `POST /posts/{id}/publish` — 게시글 공개
4. `POST /posts/{id}/comments` — 댓글 작성
5. `GET /posts?published_only=true` — 공개 게시글 조회
6. `DELETE /posts/{id}` — 게시글 삭제 (댓글도 함께)

---
## 핵심 패턴 요약

| 패턴 | 코드 |
|------|------|
| 단건 조회 후 404 | `repo.get_by_id(id)` → `if not x: raise HTTPException(404)` |
| 부분 수정 | `data.model_dump(exclude_unset=True)` |
| DB refresh | `db.commit(); db.refresh(obj)` |
| cascade 삭제 | `cascade="all, delete-orphan"` on relationship |
| 전체 수 + 목록 | `count()` + `offset().limit().all()` |
| 비즈니스 검증 | Service 계층에서 HTTPException 발생 |
| 계층 분리 | Repository는 DB 쿼리, Service는 규칙 검증, Router는 HTTP 엔드포인트, main은 앱 조립 |
