from fastapi import APIRouter, Depends

from database import admin_client
from dependencies import get_current_user
from repository import one_or_404
from schemas import CurrentUser, ProfileUpdate

router = APIRouter(tags=["Profiles"])


@router.get("/me")
def get_me(current: CurrentUser = Depends(get_current_user)):
    """인증된 현재 사용자의 프로필만 조회합니다."""

    # service_role 조회이므로 현재 사용자의 UUID를 id 조건으로 반드시 제한합니다.
    result = (
        admin_client()
        .table("profiles")
        .select("*")
        .eq("id", current.id)
        .limit(1)
        .execute()
    )
    return one_or_404(result.data, "프로필을 찾을 수 없습니다")


@router.patch("/me")
def update_me(data: ProfileUpdate, current: CurrentUser = Depends(get_current_user)):
    """인증된 현재 사용자의 표시 이름만 수정합니다."""

    # 요청에서 사용자 id를 받지 않고 JWT로 확인한 current.id를 사용합니다.
    # 따라서 다른 사용자의 id를 넣어 프로필을 수정할 수 없습니다.
    result = (
        admin_client()
        .table("profiles")
        .update({"display_name": data.display_name})
        .eq("id", current.id)
        .execute()
    )
    return one_or_404(result.data, "프로필을 찾을 수 없습니다")
