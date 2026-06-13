"""
13교시: CRUD 기반 백엔드 서비스 구현

SQLAlchemy + SQLite로 블로그 API를 완성합니다.

실행:
  pip install -r requirements.txt
  uvicorn main:app --reload

Swagger UI: http://localhost:8000/docs
"""
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="블로그 API", version="1.0.0")


# ── Repository 계층 ───────────────────────────────────────────────────────────

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cat_id: int) -> models.Category | None:
        return self.db.query(models.Category).filter(models.Category.id == cat_id).first()

    def get_by_name(self, name: str) -> models.Category | None:
        return self.db.query(models.Category).filter(models.Category.name == name).first()

    def get_all(self) -> list[models.Category]:
        return self.db.query(models.Category).all()

    def create(self, data: schemas.CategoryCreate) -> models.Category:
        cat = models.Category(**data.model_dump())
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def update(self, cat: models.Category, data: schemas.CategoryUpdate) -> models.Category:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cat, field, value)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def delete(self, cat: models.Category) -> None:
        self.db.delete(cat)
        self.db.commit()

    def count_posts(self, cat_id: int) -> int:
        return self.db.query(models.Post).filter(models.Post.category_id == cat_id).count()


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, post_id: int) -> models.Post | None:
        return self.db.query(models.Post).filter(models.Post.id == post_id).first()

    def count(
        self,
        category_id: int | None = None,
        published_only: bool = False,
        search: str | None = None,
    ) -> int:
        q = self.db.query(models.Post)
        if category_id:
            q = q.filter(models.Post.category_id == category_id)
        if published_only:
            q = q.filter(models.Post.published == True)
        if search:
            q = q.filter(models.Post.title.contains(search))
        return q.count()

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
            q = q.filter(models.Post.category_id == category_id)
        if published_only:
            q = q.filter(models.Post.published == True)
        if search:
            q = q.filter(models.Post.title.contains(search))
        return q.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, data: schemas.PostCreate) -> models.Post:
        post = models.Post(**data.model_dump())
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post: models.Post, data: schemas.PostUpdate) -> models.Post:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(post, field, value)
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: models.Post) -> None:
        self.db.delete(post)
        self.db.commit()


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_post(self, post_id: int) -> list[models.Comment]:
        return (
            self.db.query(models.Comment)
            .filter(models.Comment.post_id == post_id)
            .order_by(models.Comment.created_at.asc())
            .all()
        )

    def get_by_id(self, comment_id: int) -> models.Comment | None:
        return self.db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    def create(self, post_id: int, data: schemas.CommentCreate) -> models.Comment:
        comment = models.Comment(post_id=post_id, **data.model_dump())
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: models.Comment) -> None:
        self.db.delete(comment)
        self.db.commit()


# ── Service 계층 ──────────────────────────────────────────────────────────────

class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def list_categories(self) -> list[schemas.CategoryWithPostCount]:
        cats = self.repo.get_all()
        return [
            schemas.CategoryWithPostCount(
                id=c.id,
                name=c.name,
                description=c.description,
                post_count=len(c.posts),
            )
            for c in cats
        ]

    def create_category(self, data: schemas.CategoryCreate) -> models.Category:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
        return self.repo.create(data)

    def update_category(self, cat_id: int, data: schemas.CategoryUpdate) -> models.Category:
        cat = self.repo.get_by_id(cat_id)
        if not cat:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        if data.name and data.name != cat.name:
            if self.repo.get_by_name(data.name):
                raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
        return self.repo.update(cat, data)

    def delete_category(self, cat_id: int) -> None:
        cat = self.repo.get_by_id(cat_id)
        if not cat:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        post_count = self.repo.count_posts(cat_id)
        if post_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"게시글 {post_count}개가 속한 카테고리는 삭제할 수 없습니다",
            )
        self.repo.delete(cat)


class PostService:
    def __init__(self, db: Session):
        self.repo = PostRepository(db)
        self.category_repo = CategoryRepository(db)
        self.comment_repo = CommentRepository(db)

    def _get_or_404(self, post_id: int) -> models.Post:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
        return post

    def list_posts(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        published_only: bool = False,
        search: str | None = None,
    ) -> schemas.PaginatedPosts:
        total = self.repo.count(category_id=category_id,
                                published_only=published_only, search=search)
        items = self.repo.get_list(skip=skip, limit=limit, category_id=category_id,
                                   published_only=published_only, search=search)
        return schemas.PaginatedPosts(total=total, skip=skip, limit=limit, items=items)

    def get_post_detail(self, post_id: int) -> schemas.PostDetailResponse:
        post = self._get_or_404(post_id)
        return schemas.PostDetailResponse.model_validate(post)

    def create_post(self, data: schemas.PostCreate) -> models.Post:
        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.create(data)

    def update_post(self, post_id: int, data: schemas.PostUpdate) -> models.Post:
        post = self._get_or_404(post_id)
        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.update(post, data)

    def publish_post(self, post_id: int) -> models.Post:
        post = self._get_or_404(post_id)
        if not post.content:
            raise HTTPException(status_code=400, detail="내용이 없는 게시글은 공개할 수 없습니다")
        if post.published:
            raise HTTPException(status_code=400, detail="이미 공개된 게시글입니다")
        return self.repo.update(post, schemas.PostUpdate(published=True))

    def unpublish_post(self, post_id: int) -> models.Post:
        post = self._get_or_404(post_id)
        if not post.published:
            raise HTTPException(status_code=400, detail="이미 비공개 게시글입니다")
        return self.repo.update(post, schemas.PostUpdate(published=False))

    def delete_post(self, post_id: int) -> None:
        post = self._get_or_404(post_id)
        self.repo.delete(post)

    def add_comment(self, post_id: int, data: schemas.CommentCreate) -> models.Comment:
        post = self._get_or_404(post_id)
        if not post.published:
            raise HTTPException(status_code=400, detail="공개된 게시글에만 댓글을 달 수 있습니다")
        return self.comment_repo.create(post_id, data)

    def list_comments(self, post_id: int) -> list[models.Comment]:
        self._get_or_404(post_id)
        return self.comment_repo.get_by_post(post_id)

    def delete_comment(self, post_id: int, comment_id: int) -> None:
        self._get_or_404(post_id)
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment or comment.post_id != post_id:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다")
        self.comment_repo.delete(comment)


# ── 의존성 주입 ───────────────────────────────────────────────────────────────

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)


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
