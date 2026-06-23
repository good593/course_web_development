from fastapi import APIRouter, Depends

from database import admin_client
from dependencies import get_current_user
from repository import one_or_404
from schemas import ConversationCreate, CurrentUser

router = APIRouter(tags=["Conversations"])


@router.post("/conversations", status_code=201)
def create_conversation(
    data: ConversationCreate,
    current: CurrentUser = Depends(get_current_user),
):
    """현재 사용자를 소유자로 지정하여 새 대화방을 생성합니다."""

    # owner_id를 요청 본문에서 받지 않고 검증된 JWT 사용자 id로 강제합니다.
    result = (
        admin_client()
        .table("chat_conversations")
        .insert({"owner_id": current.id, "title": data.title})
        .execute()
    )
    return one_or_404(result.data, "대화방을 생성하지 못했습니다")


@router.get("/conversations")
def list_conversations(current: CurrentUser = Depends(get_current_user)):
    """현재 사용자가 소유한 대화방 목록만 반환합니다."""

    # service_role은 모든 행을 읽을 수 있으므로 owner_id 필터가 핵심 보안 조건입니다.
    result = (
        admin_client()
        .table("chat_conversations")
        .select("*")
        .eq("owner_id", current.id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data
