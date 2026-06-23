import asyncio
import threading
from collections.abc import AsyncIterator

from google.genai import types

from core.config import GEMINI_MODEL
from core.gemini import client
from schemas import (
    AskRequest,
    AskResponse,
    ChatRequest,
    ChatResponse,
    HistoryMessage,
    StatsResponse,
)
from services.session_store import active_session_count, get_session
from services.stats import stats


def create_generation_config(
    temperature: float,
    max_tokens: int,
    system_instruction: str | None = None,
) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        system_instruction=system_instruction,
    )


def record_usage(response) -> None:
    usage = response.usage_metadata
    stats.record(usage.prompt_token_count, usage.candidates_token_count)


async def generate_answer(req: AskRequest) -> AskResponse:
    config = create_generation_config(
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        system_instruction=req.system_instruction,
    )
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=req.question,
        config=config,
    )
    record_usage(response)
    usage = response.usage_metadata

    return AskResponse(
        answer=response.text,
        input_tokens=usage.prompt_token_count,
        output_tokens=usage.candidates_token_count,
        total_tokens=usage.total_token_count,
    )


async def stream_answer(req: AskRequest) -> AsyncIterator[str]:
    config = create_generation_config(
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        system_instruction=req.system_instruction,
    )

    async for chunk in await client.aio.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=req.question,
        config=config,
    ):
        if chunk.text:
            yield f"data: {chunk.text}\n\n"

    yield "data: [DONE]\n\n"


async def send_chat_message(session_id: str, req: ChatRequest) -> ChatResponse:
    session = get_session(session_id)
    config = create_generation_config(
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    response = await asyncio.to_thread(
        session.chat.send_message,
        req.message,
        config=config,
    )
    record_usage(response)
    usage = response.usage_metadata
    history = session.chat.get_history()

    return ChatResponse(
        session_id=session_id,
        reply=response.text,
        input_tokens=usage.prompt_token_count,
        output_tokens=usage.candidates_token_count,
        history_length=len(history),
    )


async def stream_chat_message(session_id: str, req: ChatRequest) -> AsyncIterator[str]:
    session = get_session(session_id)
    config = create_generation_config(
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[str | None] = asyncio.Queue()

    def producer() -> None:
        try:
            for chunk in session.chat.send_message_stream(req.message, config=config):
                if chunk.text:
                    asyncio.run_coroutine_threadsafe(queue.put(chunk.text), loop)
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    thread = threading.Thread(target=producer, daemon=True)
    thread.start()

    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        yield f"data: {chunk}\n\n"

    yield "data: [DONE]\n\n"


def get_chat_history(session_id: str) -> list[HistoryMessage]:
    session = get_session(session_id)
    history = session.chat.get_history()

    return [
        HistoryMessage(role=turn.role, text=turn.parts[0].text)
        for turn in history
        if turn.parts
    ]


def get_usage_stats() -> StatsResponse:
    return StatsResponse(
        total_requests=stats.total_requests,
        total_input_tokens=stats.total_input_tokens,
        total_output_tokens=stats.total_output_tokens,
        total_tokens=stats.total_input_tokens + stats.total_output_tokens,
        estimated_cost_usd=round(stats.estimated_cost(), 6),
        active_sessions=active_session_count(),
    )
