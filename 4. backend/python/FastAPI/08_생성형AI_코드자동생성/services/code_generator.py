import re
from typing import Any

from ollama import chat

from settings import CODE_MODEL, DEFAULT_OPTIONS, SYSTEM_PROMPT, THINKING_TOKEN


def get_field(value: Any, name: str, default: Any = None) -> Any:
    """Ollama 응답 객체와 dict 응답을 같은 방식으로 읽습니다."""
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def get_message_content(response: Any) -> str:
    """Ollama chat 응답에서 assistant 메시지 텍스트를 꺼냅니다."""
    message = get_field(response, "message", {})
    return get_field(message, "content", "") or ""


def strip_gemma4_thoughts(content: str) -> str:
    """다중 턴 대화 기록에 gemma4 thinking 내용을 다시 넣지 않도록 제거합니다."""
    pattern = r"<\|channel\>thought\n.*?<channel\|>"
    return re.sub(pattern, "", content, flags=re.DOTALL).strip()


def build_system_message(*, thinking: bool = False) -> dict[str, str]:
    """gemma4 thinking 모드를 켜려면 system prompt 앞에 전용 토큰을 붙입니다."""
    content = f"{THINKING_TOKEN}\n{SYSTEM_PROMPT}" if thinking else SYSTEM_PROMPT
    return {"role": "system", "content": content}


def build_messages(user_prompt: str, *, thinking: bool = False) -> list[dict[str, str]]:
    """Ollama chat API에 전달할 메시지 목록을 만듭니다."""
    return [
        build_system_message(thinking=thinking),
        {"role": "user", "content": user_prompt},
    ]


def print_stats(response: Any) -> None:
    """Ollama 응답의 로컬 실행 통계를 출력합니다."""
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
        if get_field(chunk, "done", False):
            final_chunk = chunk

        text = get_message_content(chunk)
        if not text:
            continue

        print(text, end="", flush=True)
        result.append(text)

    if final_chunk is not None:
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

    messages = build_messages(
        f"다음 API를 구현해줘:\n\n{requirements}",
        thinking=thinking,
    )
    return stream_completion(messages, num_predict=num_predict)


def extract_and_save_code(content: str, filename: str = "generated_api.py") -> bool:
    """생성된 마크다운에서 Python 코드 블록을 추출해 파일로 저장합니다."""
    pattern = r"```python\s*\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        print("Python 코드 블록을 찾지 못했습니다.")
        return False

    with open(filename, "w", encoding="utf-8") as f:
        f.write(matches[0])

    print(f"\n코드가 '{filename}'에 저장되었습니다.")
    return True


def summarize_stats_example(prompt: str) -> None:
    """짧은 비스트리밍 호출로 Ollama 로컬 실행 통계를 확인합니다."""
    completion = chat(
        model=CODE_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"다음 요구사항을 한 문장으로 요약해줘:\n\n{prompt}",
            }
        ],
        options={
            **DEFAULT_OPTIONS,
            "num_predict": 64,
        },
    )

    print(get_message_content(completion))
    print_stats(completion)


def interactive_refinement(initial_requirements: str) -> None:
    """다중 턴 대화로 코드를 반복 개선합니다."""
    conversation: list[dict[str, str]] = []

    print("\n[다중 턴 코드 생성 시작]")
    print("종료하려면 'quit' 또는 'exit'을 입력하세요.\n")

    conversation.append({"role": "user", "content": initial_requirements})
    full_response = stream_completion(
        [build_system_message(), *conversation],
    )
    print("\n")

    conversation.append(
        {"role": "assistant", "content": strip_gemma4_thoughts(full_response)}
    )

    while True:
        user_input = input("\n개선 요청 (또는 'quit'): ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})
        full_response = stream_completion(
            [build_system_message(), *conversation],
        )
        print("\n")

        conversation.append(
            {"role": "assistant", "content": strip_gemma4_thoughts(full_response)}
        )

        save = input("이 코드를 저장할까요? (y/n): ").strip().lower()
        if save == "y":
            extract_and_save_code(full_response, "refined_api.py")
