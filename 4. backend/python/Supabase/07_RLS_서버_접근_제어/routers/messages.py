from fastapi import APIRouter, Depends

from database import admin_client
from dependencies import get_current_user
from repository import get_owned_conversation, one_or_404
from schemas import CurrentUser, MessageCreate

router = APIRouter(tags=["Messages"])


@router.post("/conversations/{conversation_id}/messages", status_code=201)
def create_message(
    conversation_id: str,
    data: MessageCreate,
    current: CurrentUser = Depends(get_current_user),
):
    """현재 사용자가 소유한 대화방에 메시지를 저장합니다."""

    # 메시지를 저장하기 전에 대화방 소유권부터 확인합니다.
    # 다른 사용자의 대화방이면 존재 여부를 노출하지 않고 404를 반환합니다.
    get_owned_conversation(conversation_id, current.id)
    result = (
        admin_client()
        .table("chat_messages")
        .insert({
            "conversation_id": conversation_id,
            "owner_id": current.id,
            "role": data.role,
            "content": data.content,
        })
        .execute()
    )
    return one_or_404(result.data, "메시지를 저장하지 못했습니다")


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: str,
    current: CurrentUser = Depends(get_current_user),
):
    """현재 사용자가 소유한 대화방의 메시지만 반환합니다."""

    # 대화방 소유권을 먼저 확인한 뒤 메시지에도 owner_id 필터를 적용합니다.
    get_owned_conversation(conversation_id, current.id)
    result = (
        admin_client()
        .table("chat_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("owner_id", current.id)
        .order("created_at")
        .execute()
    )
    return result.data
