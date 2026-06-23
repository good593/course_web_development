from fastapi import APIRouter, Depends

import schemas
from core.dependencies import get_category_service
from services import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[schemas.CategoryWithPostCount],
    summary="카테고리 목록",
)
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()


@router.post(
    "",
    response_model=schemas.CategoryResponse,
    status_code=201,
    summary="카테고리 생성",
)
def create_category(data: schemas.CategoryCreate, service: CategoryService = Depends(get_category_service)):
    return service.create_category(data)


@router.patch(
    "/{cat_id}",
    response_model=schemas.CategoryResponse,
    summary="카테고리 수정",
)
def update_category(cat_id: int, data: schemas.CategoryUpdate, service: CategoryService = Depends(get_category_service)):
    return service.update_category(cat_id, data)


@router.delete(
    "/{cat_id}",
    status_code=204,
    summary="카테고리 삭제",
)
def delete_category(cat_id: int, service: CategoryService = Depends(get_category_service)):
    service.delete_category(cat_id)
