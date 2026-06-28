"""Ollama chat API를 호출해서 FastAPI 코드 초안을 생성하는 서비스 함수들입니다."""

from typing import Any

from ollama import chat

from settings import CODE_MODEL, DEFAULT_OPTIONS, SYSTEM_PROMPT, THINKING_TOKEN


def get_field(value: Any, name: str, default: Any = None) -> Any:
    """Ollama 응답 객체와 dict 응답을 같은 방식으로 읽습니다."""
    # ollama 패키지 버전이나 호출 방식에 따라 응답이 객체 또는 dict처럼 올 수 있어 둘 다 처리합니다.
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def get_message_content(response: Any) -> str:
    """Ollama chat 응답에서 assistant 메시지 텍스트를 꺼냅니다."""
    # README의 response.message.content 예시를 안전하게 읽는 헬퍼입니다.
    message = get_field(response, "message", {})
    return get_field(message, "content", "") or ""


def build_system_message(*, thinking: bool = False) -> dict[str, str]:
    """gemma4 thinking 모드를 켜려면 system prompt 앞에 전용 토큰을 붙입니다."""
    # Swagger의 thinking=true 옵션이 여기서 실제 system prompt 변경으로 이어집니다.
    content = f"{THINKING_TOKEN}\n{SYSTEM_PROMPT}" if thinking else SYSTEM_PROMPT
    return {"role": "system", "content": content}


def build_messages(user_prompt: str, *, thinking: bool = False) -> list[dict[str, str]]:
    """Ollama chat API에 전달할 메시지 목록을 만듭니다."""
    # README의 기본 API 호출 예시처럼 system 메시지와 user 메시지를 순서대로 보냅니다.
    return [
        build_system_message(thinking=thinking),
        {"role": "user", "content": user_prompt},
    ]


def print_stats(response: Any) -> None:
    """Ollama 응답의 로컬 실행 통계를 출력합니다."""
    # 비스트리밍 호출과 스트리밍 마지막 chunk에서 토큰 수와 처리 시간을 확인할 수 있습니다.
    prompt_tokens = get_field(response, "prompt_eval_count")
    output_tokens = get_field(response, "eval_count")
    total_duration = get_field(response, "total_duration")

    if prompt_tokens is not None:
        print(f"입력 토큰 추정: {prompt_tokens}")
    if output_tokens is not None:
        print(f"출력 토큰 추정: {output_tokens}")
    if total_duration is not None:
        print(f"총 소요 시간: {total_duration / 1_000_000_000:.2f}초")


def stream_completion(
    messages: list[dict[str, str]],
    *,
    num_predict: int = 8192,
) -> str:
    """Ollama 응답을 스트리밍으로 출력하고 전체 텍스트를 반환합니다."""
    # 코드 생성처럼 긴 응답은 stream=True로 받아야 콘솔에서 진행 상황을 바로 볼 수 있습니다.
    stream = chat(
        model=CODE_MODEL,
        messages=messages,
        stream=True,
        options={
            **DEFAULT_OPTIONS,
            "num_predict": num_predict,
        },
    )

    result: list[str] = []
    final_chunk = None

    for chunk in stream:
        # 마지막 chunk에는 토큰 수와 duration 같은 실행 통계가 함께 들어올 수 있습니다.
        if get_field(chunk, "done", False):
            final_chunk = chunk

        text = get_message_content(chunk)
        if not text:
            continue

        print(text, end="", flush=True)
        result.append(text)

    if final_chunk is not None:
        # README의 "로컬 실행 통계 확인" 내용을 스트리밍 호출에서도 보여 줍니다.
        print(f"\n\n{'=' * 60}")
        print_stats(final_chunk)
        print("=" * 60)

    return "".join(result)


def generate_api_code(
    requirements: str,
    *,
    thinking: bool = False,
    num_predict: int = 8192,
) -> str:
    """자연어 요구사항을 받아 FastAPI 코드를 생성합니다."""
    print("=" * 60)
    print("코드 생성 중...")
    print("=" * 60 + "\n")

    # 사용자의 자연어 요구사항을 "다음 API를 구현해줘"라는 코드 생성 프롬프트로 감쌉니다.
    messages = build_messages(
        f"다음 API를 구현해줘:\n\n{requirements}",
        thinking=thinking,
    )
    return stream_completion(messages, num_predict=num_predict)
