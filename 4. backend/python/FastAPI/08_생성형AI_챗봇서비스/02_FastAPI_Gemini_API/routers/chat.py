from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from core.config import DEFAULT_SYSTEM_INSTRUCTION
from schemas import ChatRequest, ChatResponse, HistoryMessage, SessionCreateResponse, SessionSummary
from services.gemini_service import (
    get_chat_history,
    send_chat_message,
    stream_chat_message,
)
from services.session_store import create_session, delete_session, list_active_sessions

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat/sessions",
    response_model=SessionCreateResponse,
    status_code=201,
    summary="새 대화 세션 생성",
)
async def create_chat_session(
    system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION,
):
    """새로운 대화 세션을 만듭니다. session_id를 반환합니다."""
    return create_session(system_instruction)


@router.post(
    "/chat/{session_id}",
    response_model=ChatResponse,
    summary="세션 내 메시지 전송",
)
async def chat_message(session_id: str, req: ChatRequest):
    """기존 세션에 메시지를 전송하고 대화 기록을 유지합니다."""
    return await send_chat_message(session_id, req)


@router.post("/chat/{session_id}/stream", summary="세션 스트리밍 대화")
async def chat_stream(session_id: str, req: ChatRequest):
    """세션 내 메시지를 SSE 스트리밍으로 응답합니다."""
    return StreamingResponse(
        stream_chat_message(session_id, req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get(
    "/chat/{session_id}/history",
    response_model=list[HistoryMessage],
    summary="대화 기록 조회",
)
async def get_history(session_id: str):
    """세션의 전체 대화 기록을 반환합니다."""
    return get_chat_history(session_id)


@router.delete("/chat/{session_id}", summary="세션 삭제")
async def remove_session(session_id: str):
    """세션을 삭제합니다."""
    return delete_session(session_id)


@router.get(
    "/sessions",
    response_model=list[SessionSummary],
    summary="활성 세션 목록",
)
async def list_sessions():
    """현재 활성화된 세션 목록을 반환합니다."""
    return list_active_sessions()
