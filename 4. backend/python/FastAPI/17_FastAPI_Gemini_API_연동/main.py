"""
20교시 실습: FastAPI + Gemini 연동

실행:
  pip install -r requirements.txt
  uvicorn main:app --reload

엔드포인트:
  POST /ask                         — 단순 Q&A
  POST /ask/stream                  — 스트리밍 Q&A
  POST /chat/sessions               — 새 대화 세션 생성
  POST /chat/{session_id}           — 세션 내 메시지 전송
  POST /chat/{session_id}/stream    — 세션 스트리밍
  GET  /chat/{session_id}/history   — 대화 기록
  DELETE /chat/{session_id}         — 세션 삭제
  GET  /sessions                    — 활성 세션 목록
  GET  /stats                       — 사용량 통계
"""

import asyncio
import os
import time
from dataclasses import dataclass, field
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="Gemini Chatbot API",
    description="FastAPI + Gemini 연동 실습",
    version="1.0.0",
)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.5-flash"


# ── 스키마 ─────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(500, ge=1, le=4096)
    system_instruction: str | None = None


class AskResponse(BaseModel):
    answer: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class SessionCreateResponse(BaseModel):
    session_id: str
    message: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(800, ge=1, le=4096)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    input_tokens: int
    output_tokens: int
    history_length: int


class HistoryMessage(BaseModel):
    role: str
    text: str


class StatsResponse(BaseModel):
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    active_sessions: int


# ── 세션 저장소 ────────────────────────────────────────────────────────

@dataclass
class SessionData:
    chat: object
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    system_instruction: str = "친절하고 유능한 AI 어시스턴트입니다."


sessions: dict[str, SessionData] = {}
SESSION_TTL = 3600  # 1시간


def get_session(session_id: str) -> SessionData:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}")
    session = sessions[session_id]
    session.last_used = time.time()
    return session


def cleanup_sessions():
    now = time.time()
    expired = [sid for sid, s in sessions.items() if now - s.last_used > SESSION_TTL]
    for sid in expired:
        del sessions[sid]
    return len(expired)


# ── 사용량 통계 ────────────────────────────────────────────────────────

@dataclass
class UsageStats:
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def record(self, input_tokens: int, output_tokens: int):
        self.total_requests += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def estimated_cost(self) -> float:
        return (
            self.total_input_tokens  / 1_000_000 * 0.075
            + self.total_output_tokens / 1_000_000 * 0.30
        )


stats = UsageStats()


# ── 에러 핸들러 ────────────────────────────────────────────────────────

@app.exception_handler(errors.APIError)
async def gemini_error_handler(request: Request, exc: errors.APIError):
    status_map = {429: 429, 403: 401, 400: 400}
    status_code = status_map.get(exc.status_code, 502)
    return JSONResponse(
        status_code=status_code,
        content={"detail": f"Gemini API 오류: {exc.message}"},
    )


# ── 단순 Q&A ───────────────────────────────────────────────────────────

@app.post(
    "/ask",
    response_model=AskResponse,
    summary="단순 질문/답변 (싱글턴)",
)
async def ask(req: AskRequest):
    """대화 기록 없이 단일 질문에 답변합니다."""
    config = types.GenerateContentConfig(
        temperature=req.temperature,
        max_output_tokens=req.max_tokens,
        system_instruction=req.system_instruction,
    )
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=req.question,
        config=config,
    )
    usage = response.usage_metadata
    stats.record(usage.prompt_token_count, usage.candidates_token_count)

    return AskResponse(
        answer=response.text,
        input_tokens=usage.prompt_token_count,
        output_tokens=usage.candidates_token_count,
        total_tokens=usage.total_token_count,
    )


# ── 스트리밍 Q&A ────────────────────────────────────────────────────────

@app.post("/ask/stream", summary="스트리밍 질문/답변")
async def ask_stream(req: AskRequest):
    """응답을 Server-Sent Events로 실시간 전송합니다."""
    config = types.GenerateContentConfig(
        temperature=req.temperature,
        max_output_tokens=req.max_tokens,
        system_instruction=req.system_instruction,
    )

    async def event_generator():
        async for chunk in await client.aio.models.generate_content_stream(
            model=MODEL,
            contents=req.question,
            config=config,
        ):
            if chunk.text:
                yield f"data: {chunk.text}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── 세션 생성 ─────────────────────────────────────────────────────────

@app.post(
    "/chat/sessions",
    response_model=SessionCreateResponse,
    status_code=201,
    summary="새 대화 세션 생성",
)
async def create_session(
    system_instruction: str = "친절하고 유능한 AI 어시스턴트입니다.",
):
    """새로운 대화 세션을 만듭니다. session_id를 반환합니다."""
    cleanup_sessions()

    session_id = str(uuid4())
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )
    sessions[session_id] = SessionData(
        chat=chat,
        system_instruction=system_instruction,
    )
    return SessionCreateResponse(
        session_id=session_id,
        message="세션이 생성되었습니다.",
    )


# ── 세션 내 대화 ────────────────────────────────────────────────────────

@app.post(
    "/chat/{session_id}",
    response_model=ChatResponse,
    summary="세션 내 메시지 전송",
)
async def chat_message(session_id: str, req: ChatRequest):
    """기존 세션에 메시지를 전송하고 대화 기록을 유지합니다."""
    session = get_session(session_id)

    response = await asyncio.to_thread(
        session.chat.send_message,
        req.message,
    )
    usage = response.usage_metadata
    stats.record(usage.prompt_token_count, usage.candidates_token_count)

    history = session.chat.get_history()
    return ChatResponse(
        session_id=session_id,
        reply=response.text,
        input_tokens=usage.prompt_token_count,
        output_tokens=usage.candidates_token_count,
        history_length=len(history),
    )


# ── 세션 스트리밍 ─────────────────────────────────────────────────────

@app.post("/chat/{session_id}/stream", summary="세션 스트리밍 대화")
async def chat_stream(session_id: str, req: ChatRequest):
    """세션 내 메시지를 SSE 스트리밍으로 응답합니다."""
    session = get_session(session_id)

    async def event_generator():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def producer():
            try:
                for chunk in session.chat.send_message_stream(req.message):
                    if chunk.text:
                        asyncio.run_coroutine_threadsafe(queue.put(chunk.text), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        import threading
        t = threading.Thread(target=producer, daemon=True)
        t.start()

        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── 대화 기록 조회 ─────────────────────────────────────────────────────

@app.get(
    "/chat/{session_id}/history",
    response_model=list[HistoryMessage],
    summary="대화 기록 조회",
)
async def get_history(session_id: str):
    """세션의 전체 대화 기록을 반환합니다."""
    session = get_session(session_id)
    history = session.chat.get_history()
    return [
        HistoryMessage(role=turn.role, text=turn.parts[0].text)
        for turn in history
        if turn.parts
    ]


# ── 세션 삭제 ─────────────────────────────────────────────────────────

@app.delete("/chat/{session_id}", summary="세션 삭제")
async def delete_session(session_id: str):
    """세션을 삭제합니다."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    del sessions[session_id]
    return {"message": f"세션 {session_id}가 삭제되었습니다."}


# ── 활성 세션 목록 ─────────────────────────────────────────────────────

@app.get("/sessions", summary="활성 세션 목록")
async def list_sessions():
    """현재 활성화된 세션 목록을 반환합니다."""
    now = time.time()
    return [
        {
            "session_id": sid,
            "created_ago_sec": int(now - s.created_at),
            "last_used_ago_sec": int(now - s.last_used),
            "history_turns": len(s.chat.get_history()),
        }
        for sid, s in sessions.items()
    ]


# ── 사용량 통계 ────────────────────────────────────────────────────────

@app.get("/stats", response_model=StatsResponse, summary="토큰 사용량 통계")
async def get_stats():
    """누적 토큰 사용량과 예상 비용을 반환합니다."""
    return StatsResponse(
        total_requests=stats.total_requests,
        total_input_tokens=stats.total_input_tokens,
        total_output_tokens=stats.total_output_tokens,
        total_tokens=stats.total_input_tokens + stats.total_output_tokens,
        estimated_cost_usd=round(stats.estimated_cost(), 6),
        active_sessions=len(sessions),
    )
