from fastapi import APIRouter, HTTPException

import schemas
from models.blog import blog_db

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("", response_model=list[schemas.CategoryWithPostCount], summary="카테고리 목록")
def list_categories():
    return blog_db.list_categories()


@router.post(
    "",
    response_model=schemas.CategoryResponse,
    status_code=201,
    summary="카테고리 생성",
)
def create_category(category: schemas.CategoryCreate):
    if blog_db.get_category_by_name(category.name):
        raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
    return blog_db.create_category(category)


@router.patch(
    "/{category_id}",
    response_model=schemas.CategoryResponse,
    summary="카테고리 수정",
)
def update_category(category_id: int, category: schemas.CategoryUpdate):
    current = blog_db.get_category(category_id)
    if not current:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    if category.name is not None:
        same_name = blog_db.get_category_by_name(category.name)
        if same_name and same_name["id"] != category_id:
            raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")

    return blog_db.update_category(category_id, category)


@router.delete(
    "/{category_id}",
    status_code=204,
    summary="카테고리 삭제",
)
def delete_category(category_id: int):
    if not blog_db.delete_category(category_id):
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

