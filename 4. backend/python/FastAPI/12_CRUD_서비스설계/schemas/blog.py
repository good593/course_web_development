from datetime import datetime

from pydantic import BaseModel, Field


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


# ── Post ──────────────────────────────────────────────────────────────────────

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
    category_id: int | None = None
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(PostResponse):
    category: CategoryResponse | None = None
    comment_count: int = 0


# ── Comment ───────────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    content: str
    author: str = Field(..., max_length=100)


class CommentResponse(BaseModel):
    id: int
    content: str
    author: str
    post_id: int
    created_at: datetime
