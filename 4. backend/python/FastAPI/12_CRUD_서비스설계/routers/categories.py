from fastapi import APIRouter, Depends

import schemas
from core.dependencies import get_category_service
from services import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("", response_model=list[schemas.CategoryResponse])
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()


@router.post("", response_model=schemas.CategoryResponse, status_code=201)
def create_category(
    data: schemas.CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    return service.create_category(data)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    service.delete_category(category_id)
