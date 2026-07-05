from dotenv import load_dotenv
from groq import APIStatusError, Groq

from settings import GROQ_TPM_SAFE_LIMIT, MODEL, ReasoningEffort

# .env 파일의 GROQ_API_KEY를 읽어 Groq 클라이언트가 사용할 수 있게 합니다.
load_dotenv()


class GroqGenerationError(RuntimeError):
    """Groq API로 텍스트를 생성할 수 없을 때 사용하는 예외."""


def rough_token_estimate(text: str) -> int:
    """Groq 요청 한도를 넘기지 않기 위한 보수적 근사치."""
    return max(1, len(text) // 3)


def stream_groq(
    prompt: str,
    max_tokens: int = 8192,
    reasoning_effort: ReasoningEffort = "medium",
) -> str:
    """Groq 스트리밍 응답을 끝까지 모아 하나의 문자열로 반환합니다."""
    prompt_tokens = rough_token_estimate(prompt)
    available_tokens = GROQ_TPM_SAFE_LIMIT - prompt_tokens
    if available_tokens < 512:
        raise GroqGenerationError(
            "요청 프롬프트가 현재 Groq 토큰 한도보다 큽니다. "
            "OpenAPI 스펙을 더 줄이거나 Groq 사용 한도가 높은 모델/티어를 사용하세요."
        )

    if max_tokens > available_tokens:
        # 요청 프롬프트가 길어지면 응답 토큰을 줄여서 전체 한도 안에 맞춥니다.
        max_tokens = available_tokens

    parts: list[str] = []

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

        for chunk in stream:
            # 스트리밍 응답은 작은 조각으로 오므로 빈 조각은 건너뜁니다.
            if not chunk.choices:
                continue

            text = chunk.choices[0].delta.content or ""
            if not text:
                continue

            parts.append(text)
    except APIStatusError as error:
        message = f"Groq API 요청 실패: {error.status_code}"
        if error.status_code in {413, 429}:
            message += " - 현재 모델/계정의 토큰 한도를 넘었습니다."
        raise GroqGenerationError(message) from error
    except Exception as error:
        raise GroqGenerationError(f"Groq API 요청 중 오류가 발생했습니다: {error}") from error

    return "".join(parts)
