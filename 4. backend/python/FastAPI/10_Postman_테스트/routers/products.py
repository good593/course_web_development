from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query, Security

from core.security import require_admin_token
from models.shop import shop_db
from schemas.common import COMMON_ERRORS, ErrorResponse
from schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get(
    "",
    response_model=list[ProductResponse],
    summary="상품 목록 조회",
    description="등록된 상품을 카테고리 필터와 페이지네이션으로 조회합니다.",
    response_description="상품 목록",
)
def list_products(
    category: Optional[str] = Query(default=None, description="카테고리 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
):
    return shop_db.list_products(category=category, page=page, size=size)


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
):
    if shop_db.product_name_exists(product.name):
        raise HTTPException(status_code=409, detail="동일한 상품명이 이미 존재합니다.")

    return shop_db.create_product(product)


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
):
    product = shop_db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="상품 부분 수정",
    description="상품 정보를 부분적으로 수정합니다. 전달된 필드만 업데이트됩니다.",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def update_product(product_id: int, update: ProductUpdate):
    product = shop_db.update_product(product_id, update)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="상품 삭제",
    description="상품을 삭제합니다. 삭제된 상품은 복구할 수 없습니다.",
    responses={
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def delete_product(product_id: int):
    if not shop_db.delete_product(product_id):
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
