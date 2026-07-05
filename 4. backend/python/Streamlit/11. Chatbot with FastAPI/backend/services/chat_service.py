import json
import time
from collections.abc import Iterator

from fastapi import HTTPException
from groq import AuthenticationError, Groq

from backend.core.config import GROQ_MODEL, SYSTEM_PROMPT
from backend.core.groq_client import get_client
from backend.schemas import ChatRequest, ChatResponse

GROQ_AUTH_ERROR_MESSAGE = (
    "Groq API Key가 유효하지 않거나 폐기되었습니다. "
    ".env의 GROQ_API_KEY를 Groq Console에서 새로 발급한 키로 교체하세요."
)


def is_groq_auth_error(exc: Exception) -> bool:
    return isinstance(exc, AuthenticationError) or getattr(exc, "status_code", None) == 401


def get_client_for_request() -> Groq:
    try:
        return get_client()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def build_messages(req: ChatRequest) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(message.model_dump() for message in req.history[-20:])
    messages.append({"role": "user", "content": req.message})
    return messages


def generate_reply(req: ChatRequest) -> ChatResponse:
    start = time.perf_counter()

    try:
        response = get_client_for_request().chat.completions.create(
            model=GROQ_MODEL,
            messages=build_messages(req),
            temperature=req.temperature,
            max_completion_tokens=req.max_tokens,
        )
    except HTTPException:
        raise
    except Exception as exc:
        if is_groq_auth_error(exc):
            raise HTTPException(status_code=500, detail=GROQ_AUTH_ERROR_MESSAGE) from exc
        raise HTTPException(status_code=502, detail=f"Groq API 호출 실패: {exc}") from exc

    usage = getattr(response, "usage", None)

    return ChatResponse(
        reply=response.choices[0].message.content or "",
        model=GROQ_MODEL,
        elapsed_ms=round((time.perf_counter() - start) * 1000),
        input_tokens=getattr(usage, "prompt_tokens", None),
        output_tokens=getattr(usage, "completion_tokens", None),
        total_tokens=getattr(usage, "total_tokens", None),
    )


def stream_reply(req: ChatRequest, client: Groq) -> Iterator[str]:
    try:
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=build_messages(req),
            temperature=req.temperature,
            max_completion_tokens=req.max_tokens,
            stream=True,
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                payload = json.dumps({"token": content}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        yield "data: [DONE]\n\n"
    except Exception as exc:
        message = (
            GROQ_AUTH_ERROR_MESSAGE
            if is_groq_auth_error(exc)
            else f"Groq API 호출 실패: {exc}"
        )
        payload = json.dumps({"error": message}, ensure_ascii=False)
        yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"
