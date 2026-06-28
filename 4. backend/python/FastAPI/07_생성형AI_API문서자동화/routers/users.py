from fastapi import APIRouter, Security

from core.security import require_admin_token
from schemas.common import COMMON_ERRORS, ErrorResponse
from schemas.users import UserCreate, UserResponse
from services import shop_store

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="회원 가입",
    responses={
        409: {"description": "이메일 또는 사용자명 중복", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_user(user: UserCreate) -> dict:
    return shop_store.create_user(user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
    description="Bearer 토큰으로 인증 후 현재 사용자 정보를 반환합니다.",
    responses={
        401: {"description": "인증 토큰 없음 또는 만료", "model": ErrorResponse},
    },
)
def get_me(token: str = Security(require_admin_token)) -> dict:
    # 실제 구현에서는 JWT 검증 후 토큰의 사용자 정보를 사용합니다.
    return shop_store.get_demo_user()
