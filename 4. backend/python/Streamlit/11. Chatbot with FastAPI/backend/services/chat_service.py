"""
Groq에 질문을 보내고 답변을 만드는 서비스 계층입니다.

학생 포인트:
- router는 HTTP 입구를 담당합니다.
- service는 비즈니스 로직과 외부 API 호출을 담당합니다.
"""

import json
import time
from collections.abc import Iterator

from fastapi import HTTPException
from groq import AuthenticationError, Groq

from backend.core.config import GROQ_MODEL, SYSTEM_PROMPT
from backend.core.groq_client import get_client
from backend.schemas import ChatRequest, ChatResponse

# 인증 오류는 학생들이 자주 만나는 문제라서 별도 메시지로 안내합니다.
GROQ_AUTH_ERROR_MESSAGE = (
    "Groq API Key가 유효하지 않거나 폐기되었습니다. "
    ".env의 GROQ_API_KEY를 Groq Console에서 새로 발급한 키로 교체하세요."
)


def is_groq_auth_error(exc: Exception) -> bool:
    # SDK 버전에 따라 AuthenticationError 또는 status_code=401 형태로 올 수 있습니다.
    return isinstance(exc, AuthenticationError) or getattr(exc, "status_code", None) == 401


def get_client_for_request() -> Groq:
    try:
        return get_client()
    except RuntimeError as exc:
        # 설정 오류를 FastAPI가 이해하는 HTTPException으로 바꿉니다.
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def build_messages(req: ChatRequest) -> list[dict[str, str]]:
    # Groq 채팅 API는 system -> 이전 대화 -> 현재 사용자 메시지 순서를 기대합니다.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 프론트에서 너무 긴 history를 보내도 마지막 20개만 모델에 전달합니다.
    messages.extend(message.model_dump() for message in req.history[-20:])
    messages.append({"role": "user", "content": req.message})
    return messages


def generate_reply(req: ChatRequest) -> ChatResponse:
    # 응답 시간을 측정해 학생들이 API 지연 시간을 확인할 수 있게 합니다.
    start = time.perf_counter()

    try:
        # stream=False 기본 호출입니다. 답변이 완성될 때까지 기다렸다가 한 번에 받습니다.
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
        # 외부 API 호출 실패는 백엔드 입장에서 게이트웨이 오류로 처리합니다.
        raise HTTPException(status_code=502, detail=f"Groq API 호출 실패: {exc}") from exc

    # 모델/요금제/응답 상황에 따라 usage가 없을 수도 있으므로 getattr로 안전하게 읽습니다.
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
        # stream=True를 켜면 Groq가 답변을 조각(chunk) 단위로 보내 줍니다.
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=build_messages(req),
            temperature=req.temperature,
            max_completion_tokens=req.max_tokens,
            stream=True,
        )

        for chunk in stream:
            # 각 chunk에서 새로 생성된 텍스트만 꺼냅니다.
            content = chunk.choices[0].delta.content
            if content:
                # SSE는 `data: ...\n\n` 형식으로 한 이벤트를 구분합니다.
                payload = json.dumps({"token": content}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        # 프론트엔드가 스트림 종료를 알 수 있게 마지막 신호를 보냅니다.
        yield "data: [DONE]\n\n"
    except Exception as exc:
        message = (
            GROQ_AUTH_ERROR_MESSAGE
            if is_groq_auth_error(exc)
            else f"Groq API 호출 실패: {exc}"
        )
        # 스트리밍 중 오류가 나도 SSE 형식으로 내려 보내야 프론트가 읽을 수 있습니다.
        payload = json.dumps({"error": message}, ensure_ascii=False)
        yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"
