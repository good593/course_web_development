"""
Streamlit에서 FastAPI 백엔드를 호출하는 함수들입니다.
"""

import json
from collections.abc import Iterator

import requests

from common.config import REQUEST_TIMEOUT


def health_check(api_base_url: str) -> dict:
    # 사이드바의 "FastAPI 상태 확인" 버튼에서 사용합니다.
    response = requests.get(f"{api_base_url}/health", timeout=5)
    response.raise_for_status()
    return response.json()


def parse_sse_line(line: str) -> str | None:
    # FastAPI가 보내는 SSE 줄은 `data: {...}` 형식입니다.
    if not line.startswith("data: "):
        return None

    data = line.removeprefix("data: ").strip()
    if data == "[DONE]":
        return None

    payload = json.loads(data)
    if "error" in payload:
        # 백엔드가 스트리밍 중 오류를 보내면 Streamlit 쪽 예외로 바꿉니다.
        raise RuntimeError(payload["error"])
    return payload.get("token")


def stream_answer(
    api_base_url: str,
    prompt: str,
    history: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> Iterator[str]:
    # FastAPI의 ChatRequest 스키마와 같은 모양으로 요청 본문을 만듭니다.
    payload = {
        "message": prompt,
        "history": history,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    with requests.post(
        f"{api_base_url}/chat/stream",
        json=payload,
        stream=True,
        timeout=REQUEST_TIMEOUT,
    ) as response:
        response.raise_for_status()

        # iter_lines는 서버가 보내는 SSE 줄을 하나씩 읽어 옵니다.
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            token = parse_sse_line(line)
            if token:
                # yield된 문자열은 st.write_stream()이 화면에 이어서 출력합니다.
                yield token
