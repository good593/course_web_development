import sqlite3
from typing import Any

from fastapi import HTTPException

import schemas
from repositories import CategoryRepository, CommentRepository, PostRepository


class CategoryService:
    def __init__(self, db: sqlite3.Connection):
        self.repo = CategoryRepository(db)

    def list_categories(self) -> list[dict[str, Any]]:
        return self.repo.get_all()

    def create_category(self, data: schemas.CategoryCreate) -> dict[str, Any]:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
        return self.repo.create(data)

    def delete_category(self, category_id: int) -> None:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        self.repo.delete(category_id)


class PostService:
    def __init__(self, db: sqlite3.Connection):
        self.repo = PostRepository(db)
        self.category_repo = CategoryRepository(db)
        self.comment_repo = CommentRepository(db)

    def _get_or_404(self, post_id: int) -> dict[str, Any]:
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
    ) -> list[dict[str, Any]]:
        return self.repo.get_list(
            skip=skip,
            limit=limit,
            category_id=category_id,
            published_only=published_only,
        )

    def get_post(self, post_id: int) -> dict[str, Any]:
        return self._get_or_404(post_id)

    def get_post_detail(self, post_id: int) -> dict[str, Any]:
        post = self._get_or_404(post_id)
        category_id = post["category_id"]
        category = self.category_repo.get_by_id(category_id) if category_id else None
        comment_count = len(self.comment_repo.get_by_post(post_id))
        return {
            **post,
            "category": category,
            "comment_count": comment_count,
        }

    def create_post(self, data: schemas.PostCreate) -> dict[str, Any]:
        if data.category_id is not None and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.create(data)

    def update_post(self, post_id: int, data: schemas.PostUpdate) -> dict[str, Any]:
        self._get_or_404(post_id)
        if data.category_id is not None and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.update(post_id, data)

    def publish_post(self, post_id: int) -> dict[str, Any]:
        post = self._get_or_404(post_id)
        if post["published"]:
            raise HTTPException(status_code=400, detail="이미 공개된 게시글입니다")
        return self.repo.update(post_id, schemas.PostUpdate(published=True))

    def delete_post(self, post_id: int) -> None:
        self._get_or_404(post_id)
        self.repo.delete(post_id)

    def add_comment(self, post_id: int, data: schemas.CommentCreate) -> dict[str, Any]:
        self._get_or_404(post_id)
        return self.comment_repo.create(post_id, data)

    def list_comments(self, post_id: int) -> list[dict[str, Any]]:
        self._get_or_404(post_id)
        return self.comment_repo.get_by_post(post_id)
