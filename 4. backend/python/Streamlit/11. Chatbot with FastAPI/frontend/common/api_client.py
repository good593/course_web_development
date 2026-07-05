import json
from collections.abc import Iterator

import requests

from common.config import REQUEST_TIMEOUT


def health_check(api_base_url: str) -> dict:
    response = requests.get(f"{api_base_url}/health", timeout=5)
    response.raise_for_status()
    return response.json()


def parse_sse_line(line: str) -> str | None:
    if not line.startswith("data: "):
        return None

    data = line.removeprefix("data: ").strip()
    if data == "[DONE]":
        return None

    payload = json.loads(data)
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload.get("token")


def stream_answer(
    api_base_url: str,
    prompt: str,
    history: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> Iterator[str]:
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

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            token = parse_sse_line(line)
            if token:
                yield token
