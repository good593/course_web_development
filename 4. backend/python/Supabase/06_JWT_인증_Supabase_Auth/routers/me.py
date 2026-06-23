from fastapi import APIRouter, Depends

from dependencies import get_current_user
from schemas import CurrentUser

router = APIRouter(tags=["Me"])


@router.get("/me")
def get_me(current: CurrentUser = Depends(get_current_user)):
    """유효한 Bearer 토큰을 보낸 현재 사용자의 정보를 반환합니다."""

    # Depends가 먼저 인증을 끝내므로 여기서는 검증된 사용자만 다룹니다.
    return {
        "user_id": current.id,
        "email": current.email,
        "message": "인증 성공! 이 정보는 토큰에서 읽었습니다.",
    }
