from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.schemas import ChatRequest, ChatResponse
from backend.services.chat_service import (
    generate_reply,
    get_client_for_request,
    stream_reply,
)

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse, summary="일반 챗봇 응답")
def chat(req: ChatRequest) -> ChatResponse:
    return generate_reply(req)


@router.post("/chat/stream", summary="스트리밍 챗봇 응답")
def chat_stream(req: ChatRequest) -> StreamingResponse:
    client = get_client_for_request()
    return StreamingResponse(
        stream_reply(req, client),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
