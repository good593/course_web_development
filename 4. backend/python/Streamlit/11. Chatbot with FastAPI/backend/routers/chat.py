"""
채팅 기능을 제공하는 FastAPI 라우터입니다.

라우터는 HTTP 요청/응답 모양을 담당하고, 실제 Groq 호출은 service 파일에 맡깁니다.
"""

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
    # 일반 응답은 Groq 답변이 완성된 뒤 한 번에 JSON으로 반환합니다.
    return generate_reply(req)


@router.post("/chat/stream", summary="스트리밍 챗봇 응답")
def chat_stream(req: ChatRequest) -> StreamingResponse:
    # 스트리밍 응답은 토큰이 도착할 때마다 Streamlit으로 바로 흘려보냅니다.
    client = get_client_for_request()
    return StreamingResponse(
        stream_reply(req, client),
        # text/event-stream은 SSE(Server-Sent Events) 형식이라는 뜻입니다.
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
