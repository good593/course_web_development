from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100, examples=["기술"])
    description: str | None = Field(None, max_length=500)

class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)

class CategoryWithPostCount(CategoryResponse):
    post_count: int = 0


# ── Post ──────────────────────────────────────────────────────────────────────

class PostCreate(BaseModel):
    title: str = Field(..., max_length=200, examples=["FastAPI 시작하기"])
    content: str = Field(..., examples=["FastAPI는 빠른 REST API 프레임워크입니다."])
    category_id: int | None = None

class PostUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    content: str | None = None
    summary: str | None = Field(None, max_length=500)
    published: bool | None = None
    category_id: int | None = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    published: bool
    category_id: int | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PostDetailResponse(PostResponse):
    category: CategoryResponse | None = None
    comments: list["CommentResponse"] = []


# ── Comment ───────────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    content: str = Field(..., examples=["좋은 글 감사합니다!"])
    author: str = Field(..., max_length=100, examples=["독자1"])

class CommentResponse(BaseModel):
    id: int
    content: str
    author: str
    post_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── 페이지네이션 ───────────────────────────────────────────────────────────────

class PaginatedPosts(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[PostResponse]
