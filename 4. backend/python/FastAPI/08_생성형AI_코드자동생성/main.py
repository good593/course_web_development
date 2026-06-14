"""
생성형 AI를 활용한 FastAPI 코드 자동 생성기

실행 전 Ollama를 설치하고 gemma4 모델을 내려받으세요.

    ollama pull gemma4
"""
import re
from typing import Any

from fastapi import FastAPI, HTTPException
from ollama import ResponseError, chat
from pydantic import BaseModel, Field


CODE_MODEL = "gemma4:e4b"
THINKING_TOKEN = "<|think|>"

# Ollama gemma4 페이지의 권장 샘플링 설정입니다.
DEFAULT_OPTIONS = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 64,
}

SYSTEM_PROMPT = """당신은 FastAPI 전문가입니다.
사용자의 API 요구사항을 받아 완성된 FastAPI 코드를 생성합니다.

다음 규칙을 반드시 따르세요:
1. Python 타입 힌트를 사용하세요
2. Pydantic v2 BaseModel로 입출력 스키마를 분리하세요 (Create / Update / Response)
3. HTTPException으로 404, 400, 409 등 적절한 에러를 반환하세요
4. 인메모리 dict를 DB로 사용하세요 (SQLAlchemy 사용 금지)
5. 한국어 주석을 포함하세요
6. 코드는 반드시 ```python ... ``` 블록으로 감싸세요
7. 실행 가능한 완성된 코드를 생성하세요
"""


class GenerateCodeRequest(BaseModel):
    """API 코드 생성을 요청할 때 사용하는 입력 스키마입니다."""

    requirements: str = Field(..., min_length=1, description="생성할 API 요구사항")
    thinking: bool = Field(False, description="gemma4 thinking 모드 사용 여부")
    num_predict: int = Field(8192, ge=128, le=32768, description="최대 생성 토큰 수")


class GenerateCodeResponse(BaseModel):
    """API 코드 생성 결과 응답 스키마입니다."""

    model: str
    content: str


app = FastAPI(
    title="FastAPI 코드 자동 생성기",
    description="Ollama gemma4로 FastAPI/Pydantic 코드 초안을 생성합니다.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """서버 상태와 사용 모델을 확인합니다."""
    return {
        "status": "ok",
        "model": CODE_MODEL,
        "docs": "/docs",
    }


@app.post("/generate", response_model=GenerateCodeResponse)
def generate_code_endpoint(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """요구사항을 받아 FastAPI 코드 초안을 생성합니다."""
    try:
        content = generate_api_code(
            request.requirements,
            thinking=request.thinking,
            num_predict=request.num_predict,
        )
    except ResponseError as error:
        raise HTTPException(
            status_code=502,
            detail="Ollama 호출에 실패했습니다. Ollama 실행 상태와 모델 설치 여부를 확인하세요.",
        ) from error

    return GenerateCodeResponse(model=CODE_MODEL, content=content)


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

    # 1턴: 초기 코드 생성
    conversation.append({"role": "user", "content": initial_requirements})
    full_response = stream_completion(
        [build_system_message(), *conversation],
    )
    print("\n")

    conversation.append(
        {"role": "assistant", "content": strip_gemma4_thoughts(full_response)}
    )

    # 이후 턴: 사용자 피드백 반영
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


# -- 예제 요구사항 ------------------------------------------------------------

EXAMPLE_SIMPLE = """
블로그 게시글 관리 API:
- POST /posts: 게시글 작성 (title, content, author 필수)
- GET /posts: 전체 목록 조회
- GET /posts/{post_id}: 특정 게시글 조회
- PUT /posts/{post_id}: 게시글 수정
- DELETE /posts/{post_id}: 게시글 삭제

추가 요구사항:
- 존재하지 않는 게시글 404 처리
- created_at 타임스탬프 자동 부여
- PostCreate, PostUpdate, PostResponse 스키마 분리
"""

EXAMPLE_COMPLEX = """
전자상거래 주문 API:

[데이터 구조]
- Product: id, name, price(원), stock(재고 수량)
- Order: id, user_id, items(List), total_price, status, created_at
- OrderItem: product_id, quantity, unit_price

[엔드포인트]
- GET /products: 상품 목록
- POST /orders: 주문 생성
- GET /orders/{order_id}: 주문 조회
- PATCH /orders/{order_id}/cancel: 주문 취소

[비즈니스 규칙]
1. 주문 생성 시 재고 확인 (부족하면 400)
2. 재고 차감은 주문 생성 후 즉시
3. 취소는 'pending' 상태에서만 가능 (그 외 400)
4. 취소 시 재고 복구
5. total_price는 서버에서 계산 (클라이언트 입력 무시)
"""


def main() -> None:
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "simple"

    try:
        if mode == "simple":
            # 단순 코드 생성
            print(f"프롬프트 글자 수: {len(EXAMPLE_SIMPLE):,}\n")
            generated = generate_api_code(EXAMPLE_SIMPLE)
            extract_and_save_code(generated, "generated_blog_api.py")

        elif mode == "complex":
            # 복잡한 코드 생성: gemma4 thinking 모드 활용
            generated = generate_api_code(EXAMPLE_COMPLEX, thinking=True)
            extract_and_save_code(generated, "generated_order_api.py")

        elif mode == "interactive":
            # 다중 턴 대화로 코드 개선
            custom_requirements = """
            사용자 관리 API (username, email, password 필드)
            CRUD 기능 + 비밀번호 변경 엔드포인트 포함
            """
            interactive_refinement(custom_requirements)

        elif mode == "usage":
            # 짧은 비스트리밍 호출로 로컬 실행 통계 확인
            summarize_stats_example(EXAMPLE_SIMPLE)

        else:
            print("사용법: python main.py [simple|complex|interactive|usage]")

    except ResponseError as error:
        print(f"\nOllama 호출 실패: {error}")
        print("Ollama가 실행 중인지, `ollama pull gemma4`를 먼저 실행했는지 확인하세요.")
        raise


if __name__ == "__main__":
    main()
