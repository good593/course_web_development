from fastapi import APIRouter, Path

from schemas.common import COMMON_ERRORS, ErrorResponse
from schemas.orders import OrderCreate, OrderResponse
from services import shop_store

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
    summary="주문 생성",
    description="상품을 주문합니다. 재고 확인 후 자동으로 재고가 차감됩니다.",
    responses={
        400: {"description": "재고 부족", "model": ErrorResponse},
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_order(order: OrderCreate) -> dict:
    return shop_store.create_order(order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="주문 조회",
    responses={404: {"description": "주문을 찾을 수 없음", "model": ErrorResponse}},
)
def get_order(order_id: int = Path(description="조회할 주문 ID", ge=1)) -> dict:
    return shop_store.get_order(order_id)
