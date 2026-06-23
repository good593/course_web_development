import sqlite3

from fastapi import Depends

from core.database import get_db
from services import CategoryService, PostService


def get_category_service(db: sqlite3.Connection = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_post_service(db: sqlite3.Connection = Depends(get_db)) -> PostService:
    return PostService(db)
