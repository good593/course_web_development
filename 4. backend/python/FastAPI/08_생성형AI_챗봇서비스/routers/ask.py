from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from schemas import AskRequest, AskResponse
from services.gemini_service import generate_answer, stream_answer

router = APIRouter(tags=["Ask"])


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="단순 질문/답변 (싱글턴)",
)
async def ask(req: AskRequest):
    """대화 기록 없이 단일 질문에 답변합니다."""
    return await generate_answer(req)


@router.post("/ask/stream", summary="스트리밍 질문/답변")
async def ask_stream(req: AskRequest):
    """응답을 Server-Sent Events로 실시간 전송합니다."""
    return StreamingResponse(
        stream_answer(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
