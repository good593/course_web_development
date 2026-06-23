from fastapi import APIRouter, Depends

from dependencies import get_current_session
from schemas import AppSession, ConversationCreate
from supabase_db.client import admin_client
from supabase_db.repository import one_or_404

router = APIRouter(tags=["Conversations"])


@router.post("/conversations", status_code=201)
def create_conversation(
    data: ConversationCreate,
    session: AppSession = Depends(get_current_session),
):
    result = (
        admin_client()
        .table("chat_conversations")
        .insert({"owner_id": session.user_id, "title": data.title})
        .execute()
    )
    return one_or_404(result.data, "대화방을 생성하지 못했습니다")


@router.get("/conversations")
def list_conversations(session: AppSession = Depends(get_current_session)):
    result = (
        admin_client()
        .table("chat_conversations")
        .select("*")
        .eq("owner_id", session.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data
