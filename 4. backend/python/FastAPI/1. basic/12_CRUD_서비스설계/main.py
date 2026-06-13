"""
12교시: CRUD 기반 백엔드 서비스 설계

Repository / Service 패턴을 인메모리 저장소로 시연합니다.
DB 없이 실행 가능하며, 13교시에서 SQLAlchemy로 교체합니다.

실행: uvicorn main:app --reload
"""
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="블로그 API — 설계 패턴 데모")


# ── 도메인 모델 ───────────────────────────────────────────────────────────────

class Category:
    def __init__(self, id: int, name: str, description: str | None = None):
        self.id = id
        self.name = name
        self.description = description


class Post:
    def __init__(
        self,
        id: int,
        title: str,
        content: str,
        category_id: int | None = None,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.summary: str | None = None
        self.published: bool = False
        self.category_id = category_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class Comment:
    def __init__(self, id: int, content: str, author: str, post_id: int):
        self.id = id
        self.content = content
        self.author = author
        self.post_id = post_id
        self.created_at = datetime.utcnow()


# ── Pydantic 스키마 ───────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    category_id: int | None = None

class PostUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    content: str | None = None
    summary: str | None = None
    published: bool | None = None
    category_id: int | None = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    published: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PostDetailResponse(PostResponse):
    category: CategoryResponse | None = None
    comment_count: int = 0


class CommentCreate(BaseModel):
    content: str
    author: str = Field(..., max_length=100)

class CommentResponse(BaseModel):
    id: int
    content: str
    author: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── 인메모리 저장소 (13교시에서 SQLAlchemy로 교체) ──────────────────────────────

class InMemoryDB:
    def __init__(self):
        self.categories: dict[int, Category] = {}
        self.posts: dict[int, Post] = {}
        self.comments: dict[int, Comment] = {}
        self._cat_seq = 0
        self._post_seq = 0
        self._comment_seq = 0

    def next_cat_id(self) -> int:
        self._cat_seq += 1
        return self._cat_seq

    def next_post_id(self) -> int:
        self._post_seq += 1
        return self._post_seq

    def next_comment_id(self) -> int:
        self._comment_seq += 1
        return self._comment_seq


db = InMemoryDB()


def get_db() -> InMemoryDB:
    return db


# ── Repository 계층 ───────────────────────────────────────────────────────────

class CategoryRepository:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def get_by_id(self, cat_id: int) -> Category | None:
        return self.db.categories.get(cat_id)

    def get_by_name(self, name: str) -> Category | None:
        return next((c for c in self.db.categories.values() if c.name == name), None)

    def get_all(self) -> list[Category]:
        return list(self.db.categories.values())

    def create(self, data: CategoryCreate) -> Category:
        cat = Category(id=self.db.next_cat_id(), **data.model_dump())
        self.db.categories[cat.id] = cat
        return cat

    def delete(self, cat: Category) -> None:
        del self.db.categories[cat.id]


class PostRepository:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def get_by_id(self, post_id: int) -> Post | None:
        return self.db.posts.get(post_id)

    def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        published_only: bool = False,
    ) -> list[Post]:
        posts = list(self.db.posts.values())
        if category_id is not None:
            posts = [p for p in posts if p.category_id == category_id]
        if published_only:
            posts = [p for p in posts if p.published]
        posts.sort(key=lambda p: p.created_at, reverse=True)
        return posts[skip: skip + limit]

    def create(self, data: PostCreate) -> Post:
        post = Post(id=self.db.next_post_id(), **data.model_dump())
        self.db.posts[post.id] = post
        return post

    def update(self, post: Post, data: PostUpdate) -> Post:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(post, field, value)
        post.updated_at = datetime.utcnow()
        return post

    def delete(self, post: Post) -> None:
        # cascade: 연관 댓글 삭제
        to_delete = [cid for cid, c in self.db.comments.items() if c.post_id == post.id]
        for cid in to_delete:
            del self.db.comments[cid]
        del self.db.posts[post.id]


class CommentRepository:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def get_by_post(self, post_id: int) -> list[Comment]:
        return [c for c in self.db.comments.values() if c.post_id == post_id]

    def get_by_id(self, comment_id: int) -> Comment | None:
        return self.db.comments.get(comment_id)

    def create(self, post_id: int, data: CommentCreate) -> Comment:
        comment = Comment(
            id=self.db.next_comment_id(),
            post_id=post_id,
            **data.model_dump(),
        )
        self.db.comments[comment.id] = comment
        return comment

    def delete(self, comment: Comment) -> None:
        del self.db.comments[comment.id]


# ── Service 계층 ──────────────────────────────────────────────────────────────

class CategoryService:
    def __init__(self, db: InMemoryDB):
        self.repo = CategoryRepository(db)

    def list_categories(self) -> list[Category]:
        return self.repo.get_all()

    def create_category(self, data: CategoryCreate) -> Category:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
        return self.repo.create(data)

    def delete_category(self, cat_id: int) -> None:
        cat = self.repo.get_by_id(cat_id)
        if not cat:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        self.repo.delete(cat)


class PostService:
    def __init__(self, db: InMemoryDB):
        self.repo = PostRepository(db)
        self.category_repo = CategoryRepository(db)
        self.comment_repo = CommentRepository(db)

    def _get_or_404(self, post_id: int) -> Post:
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
    ) -> list[Post]:
        return self.repo.get_list(skip=skip, limit=limit,
                                  category_id=category_id, published_only=published_only)

    def get_post(self, post_id: int) -> Post:
        return self._get_or_404(post_id)

    def create_post(self, data: PostCreate) -> Post:
        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.create(data)

    def update_post(self, post_id: int, data: PostUpdate) -> Post:
        post = self._get_or_404(post_id)
        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.update(post, data)

    def publish_post(self, post_id: int) -> Post:
        post = self._get_or_404(post_id)
        if post.published:
            raise HTTPException(status_code=400, detail="이미 공개된 게시글입니다")
        return self.repo.update(post, PostUpdate(published=True))

    def delete_post(self, post_id: int) -> None:
        post = self._get_or_404(post_id)
        self.repo.delete(post)

    def add_comment(self, post_id: int, data: CommentCreate) -> Comment:
        self._get_or_404(post_id)
        return self.comment_repo.create(post_id, data)

    def list_comments(self, post_id: int) -> list[Comment]:
        self._get_or_404(post_id)
        return self.comment_repo.get_by_post(post_id)


# ── 의존성 주입 팩토리 ──────────────────────────────────────────────────────────

def get_category_service(storage: InMemoryDB = Depends(get_db)) -> CategoryService:
    return CategoryService(storage)

def get_post_service(storage: InMemoryDB = Depends(get_db)) -> PostService:
    return PostService(storage)


# ── 라우터 ────────────────────────────────────────────────────────────────────

# Category 엔드포인트
@app.get("/categories", response_model=list[CategoryResponse], tags=["Categories"])
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()

@app.post("/categories", response_model=CategoryResponse, status_code=201, tags=["Categories"])
def create_category(data: CategoryCreate, service: CategoryService = Depends(get_category_service)):
    return service.create_category(data)

@app.delete("/categories/{cat_id}", status_code=204, tags=["Categories"])
def delete_category(cat_id: int, service: CategoryService = Depends(get_category_service)):
    service.delete_category(cat_id)


# Post 엔드포인트
@app.get("/posts", response_model=list[PostResponse], tags=["Posts"])
def list_posts(
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    published_only: bool = False,
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(skip=skip, limit=limit,
                              category_id=category_id, published_only=published_only)

@app.get("/posts/{post_id}", response_model=PostDetailResponse, tags=["Posts"])
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    post = service.get_post(post_id)
    category = service.category_repo.get_by_id(post.category_id) if post.category_id else None
    comment_count = len(service.comment_repo.get_by_post(post_id))
    response = PostDetailResponse(
        id=post.id, title=post.title, content=post.content,
        summary=post.summary, published=post.published, created_at=post.created_at,
        category=category, comment_count=comment_count,
    )
    return response

@app.post("/posts", response_model=PostResponse, status_code=201, tags=["Posts"])
def create_post(data: PostCreate, service: PostService = Depends(get_post_service)):
    return service.create_post(data)

@app.patch("/posts/{post_id}", response_model=PostResponse, tags=["Posts"])
def update_post(post_id: int, data: PostUpdate, service: PostService = Depends(get_post_service)):
    return service.update_post(post_id, data)

@app.post("/posts/{post_id}/publish", response_model=PostResponse, tags=["Posts"])
def publish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.publish_post(post_id)

@app.delete("/posts/{post_id}", status_code=204, tags=["Posts"])
def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    service.delete_post(post_id)


# Comment 엔드포인트
@app.get("/posts/{post_id}/comments", response_model=list[CommentResponse], tags=["Comments"])
def list_comments(post_id: int, service: PostService = Depends(get_post_service)):
    return service.list_comments(post_id)

@app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201, tags=["Comments"])
def add_comment(post_id: int, data: CommentCreate, service: PostService = Depends(get_post_service)):
    return service.add_comment(post_id, data)


# ── 초기 데이터 ───────────────────────────────────────────────────────────────

@app.on_event("startup")
def seed_data():
    cat_svc = CategoryService(db)
    post_svc = PostService(db)

    tech = cat_svc.create_category(CategoryCreate(name="기술", description="개발 관련 글"))
    life = cat_svc.create_category(CategoryCreate(name="일상", description="일상 이야기"))

    p1 = post_svc.create_post(PostCreate(
        title="FastAPI 시작하기",
        content="FastAPI는 Python으로 REST API를 빠르게 만들 수 있는 프레임워크입니다.",
        category_id=tech.id,
    ))
    post_svc.publish_post(p1.id)

    p2 = post_svc.create_post(PostCreate(
        title="SQLAlchemy 기초",
        content="SQLAlchemy ORM을 사용하면 Python 코드로 DB를 조작할 수 있습니다.",
        category_id=tech.id,
    ))
    post_svc.add_comment(p1.id, CommentCreate(content="좋은 글 감사합니다!", author="독자1"))
    post_svc.add_comment(p1.id, CommentCreate(content="많은 도움이 됐어요.", author="독자2"))
    _ = p2  # 게시글2는 미공개 상태로 유지
