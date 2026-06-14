"""
13교시: CRUD 기반 백엔드 서비스 구현

SQLAlchemy + SQLite로 블로그 API를 완성합니다.

실행:
  pip install -r requirements.txt
  uvicorn main:app --reload

Swagger UI: http://localhost:8000/docs
"""
from fastapi import Depends, FastAPI, Query

import schemas
from database import Base, engine
from dependencies import get_category_service, get_post_service
from services import CategoryService, PostService

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="블로그 API", version="1.0.0")


# ── 엔드포인트 — Categories ───────────────────────────────────────────────────

@app.get(
    "/categories",
    response_model=list[schemas.CategoryWithPostCount],
    tags=["Categories"],
    summary="카테고리 목록",
)
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()

@app.post(
    "/categories",
    response_model=schemas.CategoryResponse,
    status_code=201,
    tags=["Categories"],
    summary="카테고리 생성",
)
def create_category(data: schemas.CategoryCreate, service: CategoryService = Depends(get_category_service)):
    return service.create_category(data)

@app.patch(
    "/categories/{cat_id}",
    response_model=schemas.CategoryResponse,
    tags=["Categories"],
    summary="카테고리 수정",
)
def update_category(cat_id: int, data: schemas.CategoryUpdate, service: CategoryService = Depends(get_category_service)):
    return service.update_category(cat_id, data)

@app.delete(
    "/categories/{cat_id}",
    status_code=204,
    tags=["Categories"],
    summary="카테고리 삭제",
)
def delete_category(cat_id: int, service: CategoryService = Depends(get_category_service)):
    service.delete_category(cat_id)


# ── 엔드포인트 — Posts ────────────────────────────────────────────────────────

@app.get(
    "/posts",
    response_model=schemas.PaginatedPosts,
    tags=["Posts"],
    summary="게시글 목록 (페이징, 검색, 필터)",
)
def list_posts(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 항목 수"),
    category_id: int | None = Query(None, description="카테고리 필터"),
    published_only: bool = Query(False, description="공개 게시글만"),
    search: str | None = Query(None, description="제목 키워드 검색"),
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(
        skip=skip, limit=limit, category_id=category_id,
        published_only=published_only, search=search,
    )

@app.get(
    "/posts/{post_id}",
    response_model=schemas.PostDetailResponse,
    tags=["Posts"],
    summary="게시글 상세 (카테고리 + 댓글 포함)",
)
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.get_post_detail(post_id)

@app.post(
    "/posts",
    response_model=schemas.PostResponse,
    status_code=201,
    tags=["Posts"],
    summary="게시글 생성",
)
def create_post(data: schemas.PostCreate, service: PostService = Depends(get_post_service)):
    return service.create_post(data)

@app.patch(
    "/posts/{post_id}",
    response_model=schemas.PostResponse,
    tags=["Posts"],
    summary="게시글 수정",
)
def update_post(post_id: int, data: schemas.PostUpdate, service: PostService = Depends(get_post_service)):
    return service.update_post(post_id, data)

@app.post(
    "/posts/{post_id}/publish",
    response_model=schemas.PostResponse,
    tags=["Posts"],
    summary="게시글 공개",
)
def publish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.publish_post(post_id)

@app.post(
    "/posts/{post_id}/unpublish",
    response_model=schemas.PostResponse,
    tags=["Posts"],
    summary="게시글 비공개",
)
def unpublish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.unpublish_post(post_id)

@app.delete(
    "/posts/{post_id}",
    status_code=204,
    tags=["Posts"],
    summary="게시글 삭제 (댓글 포함)",
)
def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    service.delete_post(post_id)


# ── 엔드포인트 — Comments ─────────────────────────────────────────────────────

@app.get(
    "/posts/{post_id}/comments",
    response_model=list[schemas.CommentResponse],
    tags=["Comments"],
    summary="게시글 댓글 목록",
)
def list_comments(post_id: int, service: PostService = Depends(get_post_service)):
    return service.list_comments(post_id)

@app.post(
    "/posts/{post_id}/comments",
    response_model=schemas.CommentResponse,
    status_code=201,
    tags=["Comments"],
    summary="댓글 작성 (공개 게시글만)",
)
def add_comment(post_id: int, data: schemas.CommentCreate, service: PostService = Depends(get_post_service)):
    return service.add_comment(post_id, data)

@app.delete(
    "/posts/{post_id}/comments/{comment_id}",
    status_code=204,
    tags=["Comments"],
    summary="댓글 삭제",
)
def delete_comment(post_id: int, comment_id: int, service: PostService = Depends(get_post_service)):
    service.delete_comment(post_id, comment_id)
