from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from services import CategoryService, PostService


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)
