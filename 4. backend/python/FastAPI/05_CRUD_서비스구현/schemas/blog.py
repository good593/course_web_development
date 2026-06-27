from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["기술"])
    description: str | None = Field(
        default=None,
        max_length=500,
        examples=["FastAPI, Python, 데이터베이스 관련 글"],
    )


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime


class CategoryWithPostCount(CategoryResponse):
    post_count: int = 0


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["FastAPI와 SQLite로 CRUD 만들기"])
    content: str = Field(..., min_length=1, examples=["sqlite3 표준 라이브러리로 게시글을 저장합니다."])
    summary: str | None = Field(default=None, max_length=500, examples=["SQLite 기반 CRUD 실습"])
    published: bool = Field(default=False, description="공개 여부")
    category_id: int | None = Field(default=None, description="연결할 카테고리 ID")


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    summary: str | None = Field(default=None, max_length=500)
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


class PaginatedPosts(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[PostResponse]

