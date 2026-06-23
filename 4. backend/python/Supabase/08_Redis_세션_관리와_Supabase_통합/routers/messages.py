import json

from fastapi import APIRouter, Depends

from config import RECENT_HISTORY_LIMIT
from dependencies import get_current_session
from redis_cache.client import r, recent_history_key
from redis_cache.history import append_recent_message
from schemas import AppSession, MessageCreate
from supabase_db.client import admin_client
from supabase_db.repository import get_owned_conversation, one_or_404

router = APIRouter(tags=["Messages"])


@router.post("/conversations/{conversation_id}/messages", status_code=201)
def create_message(
    conversation_id: str,
    data: MessageCreate,
    session: AppSession = Depends(get_current_session),
):
    # Supabase DB: 소유권 확인 후 메시지를 영구 저장합니다.
    get_owned_conversation(conversation_id, session.user_id)
    result = (
        admin_client()
        .table("chat_messages")
        .insert({
            "conversation_id": conversation_id,
            "owner_id": session.user_id,
            "role": data.role,
            "content": data.content,
        })
        .execute()
    )
    message = one_or_404(result.data, "메시지를 저장하지 못했습니다")
    # Redis: 영구 저장 성공 후 최근 대화 캐시를 갱신합니다.
    append_recent_message(session.user_id, conversation_id, message)
    return message


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    # 전체 대화 이력은 캐시가 아닌 Supabase DB에서 시간순으로 조회합니다.
    get_owned_conversation(conversation_id, session.user_id)
    result = (
        admin_client()
        .table("chat_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("owner_id", session.user_id)
        .order("created_at")
        .execute()
    )
    return result.data


@router.get("/conversations/{conversation_id}/recent")
def recent_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    # Redis: LLM 컨텍스트 등에 사용할 최근 N개를 빠르게 조회합니다.
    get_owned_conversation(conversation_id, session.user_id)
    key = recent_history_key(session.user_id, conversation_id)
    return [json.loads(item) for item in r.lrange(key, 0, -1)]


@router.post("/conversations/{conversation_id}/recent/rebuild")
def rebuild_recent_messages(
    conversation_id: str,
    session: AppSession = Depends(get_current_session),
):
    get_owned_conversation(conversation_id, session.user_id)
    # Supabase DB: 최신 N개를 내림차순으로 조회합니다.
    result = (
        admin_client()
        .table("chat_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("owner_id", session.user_id)
        .order("created_at", desc=True)
        .limit(RECENT_HISTORY_LIMIT)
        .execute()
    )
    # Redis: List에는 오래된 메시지부터 넣기 위해 조회 결과를 뒤집습니다.
    messages = list(reversed(result.data))
    key = recent_history_key(session.user_id, conversation_id)
    # 기존 캐시를 지운 뒤 Supabase 원본으로 완전히 재생성합니다.
    r.delete(key)
    for message in messages:
        append_recent_message(session.user_id, conversation_id, message)
    return {"rebuilt": len(messages), "recent_key": key}
