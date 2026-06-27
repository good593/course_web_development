import sys

from dotenv import load_dotenv
from groq import APIStatusError, Groq

from settings import GROQ_TPM_SAFE_LIMIT, MODEL, ReasoningEffort

load_dotenv()


def rough_token_estimate(text: str) -> int:
    """Groq 요청 한도를 넘기지 않기 위한 보수적 근사치."""
    return max(1, len(text) // 3)


def stream_groq(
    prompt: str,
    max_tokens: int = 8192,
    reasoning_effort: ReasoningEffort = "medium",
) -> str:
    prompt_tokens = rough_token_estimate(prompt)
    available_tokens = GROQ_TPM_SAFE_LIMIT - prompt_tokens
    if available_tokens < 512:
        print("요청 프롬프트가 현재 Groq 토큰 한도보다 큽니다.")
        print("OpenAPI 스펙을 더 줄이거나 Groq 사용 한도가 높은 모델/티어를 사용하세요.")
        sys.exit(1)

    if max_tokens > available_tokens:
        max_tokens = available_tokens
        print(f"현재 Groq 한도에 맞춰 출력 토큰을 {max_tokens}개로 조정합니다.")

    try:
        client = Groq()
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=max_tokens,
            reasoning_effort=reasoning_effort,
            reasoning_format="hidden",
            temperature=0.2,
            stream=True,
        )
    except APIStatusError as error:
        print(f"Groq API 요청 실패: {error.status_code}")
        if error.status_code in {413, 429}:
            print("현재 모델/계정의 토큰 한도를 넘었습니다.")
            print("잠시 후 다시 실행하거나, 더 작은 명령(docs/readme 등)으로 나눠 실행하세요.")
        else:
            print(error)
        sys.exit(1)

    parts: list[str] = []
    usage = None

    for chunk in stream:
        chunk_usage = getattr(chunk, "usage", None)
        if chunk_usage is not None:
            usage = chunk_usage

        if not chunk.choices:
            continue

        text = chunk.choices[0].delta.content or ""
        if not text:
            continue

        print(text, end="", flush=True)
        parts.append(text)

    print()
    if usage is not None:
        print(f"입력 토큰: {usage.prompt_tokens} / 출력 토큰: {usage.completion_tokens}")
        print(f"총 토큰: {usage.total_tokens}")

    return "".join(parts)
