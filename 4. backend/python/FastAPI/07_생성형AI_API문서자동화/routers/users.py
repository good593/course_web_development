from fastapi import APIRouter, Security

from core.security import require_admin_token
from schemas.common import COMMON_ERRORS, ErrorResponse
from schemas.users import UserCreate, UserResponse
from services import shop_store

# 회원 관련 엔드포인트는 모두 /users 아래에 모입니다.
router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="회원 가입",
    responses={
        409: {"description": "이메일 중복", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_user(user: UserCreate) -> dict:
    # 가입 요청의 중복 검사와 저장은 서비스 계층에서 처리합니다.
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
    # 여기서는 인증 흐름을 보여 주기 위해 데모 사용자를 반환합니다.
    return shop_store.get_demo_user()
