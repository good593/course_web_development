from sqlalchemy.orm import Session

import models
import schemas


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
