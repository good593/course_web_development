from typing import List, Optional

from fastapi import APIRouter, Path, Query, Security

from core.security import require_admin_token
from schemas.common import COMMON_ERRORS, ErrorResponse
from schemas.products import ProductCreate, ProductResponse, ProductUpdate
from services import shop_store

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=List[ProductResponse],
    summary="상품 목록 조회",
    description="등록된 상품을 카테고리 필터와 페이지네이션으로 조회합니다.",
    response_description="상품 목록",
)
def list_products(
    category: Optional[str] = Query(default=None, description="카테고리 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
) -> list[dict]:
    return shop_store.list_products(category=category, page=page, size=size)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
    summary="상품 등록",
    description="새 상품을 등록합니다. 관리자 권한이 필요합니다.",
    response_description="등록된 상품 정보",
    responses={
        409: {"description": "동일한 상품명이 이미 존재함", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_product(
    product: ProductCreate,
    token: str = Security(require_admin_token),
) -> dict:
    # token 매개변수는 Swagger의 Authorize 버튼과 OpenAPI security 정보를 만들기 위해 둡니다.
    return shop_store.create_product(product)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="상품 단건 조회",
    description="ID로 특정 상품의 상세 정보를 조회합니다.",
    response_description="조회된 상품 정보",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def get_product(
    product_id: int = Path(description="조회할 상품 ID", ge=1, examples={"기본 예시": {"value": 1}}),
) -> dict:
    return shop_store.get_product(product_id)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="상품 부분 수정",
    description="상품 정보를 부분적으로 수정합니다. 전달된 필드만 업데이트되며 관리자 권한이 필요합니다.",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def update_product(
    product_id: int,
    update: ProductUpdate,
    token: str = Security(require_admin_token),
) -> dict:
    return shop_store.update_product(product_id, update)


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="상품 삭제",
    description="상품을 삭제합니다. 삭제된 상품은 복구할 수 없으며 관리자 권한이 필요합니다.",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def delete_product(
    product_id: int,
    token: str = Security(require_admin_token),
) -> None:
    shop_store.delete_product(product_id)
