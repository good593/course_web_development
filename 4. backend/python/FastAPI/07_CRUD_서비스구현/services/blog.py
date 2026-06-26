from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from repositories import CategoryRepository, CommentRepository, PostRepository


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
        total = self.repo.count(
            category_id=category_id,
            published_only=published_only,
            search=search,
        )
        items = self.repo.get_list(
            skip=skip,
            limit=limit,
            category_id=category_id,
            published_only=published_only,
            search=search,
        )
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
