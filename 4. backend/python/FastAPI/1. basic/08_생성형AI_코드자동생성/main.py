"""
생성형 AI를 활용한 FastAPI 코드 자동 생성기

실행 전 .env 파일에 ANTHROPIC_API_KEY를 설정하세요.
"""
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

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


def generate_api_code(requirements: str, use_thinking: bool = True) -> str:
    """자연어 요구사항을 받아 FastAPI 코드를 생성합니다."""
    print("=" * 60)
    print("코드 생성 중...")
    print("=" * 60 + "\n")

    thinking_option = {"type": "adaptive"} if use_thinking else {"type": "disabled"}

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=8192,
        thinking=thinking_option,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"다음 API를 구현해줘:\n\n{requirements}"}
        ],
    ) as stream:
        result = []
        for text in stream.text_stream:
            print(text, end="", flush=True)
            result.append(text)

    final = stream.get_final_message()
    print(f"\n\n{'=' * 60}")
    print(f"입력 토큰: {final.usage.input_tokens} / 출력 토큰: {final.usage.output_tokens}")
    print("=" * 60)

    return "".join(result)


def extract_and_save_code(content: str, filename: str = "generated_api.py") -> bool:
    """생성된 마크다운에서 Python 코드 블록을 추출해 파일로 저장합니다."""
    pattern = r"```python\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        print("Python 코드 블록을 찾지 못했습니다.")
        return False

    with open(filename, "w", encoding="utf-8") as f:
        f.write(matches[0])

    print(f"\n코드가 '{filename}'에 저장되었습니다.")
    return True


def estimate_tokens(prompt: str) -> int:
    """API 호출 전 입력 토큰 수를 추정합니다."""
    count = client.messages.count_tokens(
        model="claude-opus-4-8",
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return count.input_tokens


def interactive_refinement(initial_requirements: str):
    """다중 턴 대화로 코드를 반복 개선합니다."""
    conversation = []

    print("\n[다중 턴 코드 생성 시작]")
    print("종료하려면 'quit' 또는 'exit'을 입력하세요.\n")

    # 1턴: 초기 코드 생성
    conversation.append({"role": "user", "content": initial_requirements})

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=conversation,
    ) as stream:
        response_parts = []
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response_parts.append(text)
    print("\n")

    full_response = "".join(response_parts)
    conversation.append({"role": "assistant", "content": full_response})

    # 이후 턴: 사용자 피드백 반영
    while True:
        user_input = input("\n개선 요청 (또는 'quit'): ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})

        with client.messages.stream(
            model="claude-opus-4-8",
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=conversation,
        ) as stream:
            response_parts = []
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_parts.append(text)
        print("\n")

        full_response = "".join(response_parts)
        conversation.append({"role": "assistant", "content": full_response})

        save = input("이 코드를 저장할까요? (y/n): ").strip().lower()
        if save == "y":
            extract_and_save_code(full_response, "refined_api.py")


# ── 예제 요구사항 ─────────────────────────────────────────────────────────────

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


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "simple"

    if mode == "simple":
        # 단순 코드 생성
        estimated = estimate_tokens(EXAMPLE_SIMPLE)
        print(f"예상 입력 토큰: {estimated}\n")
        generated = generate_api_code(EXAMPLE_SIMPLE)
        extract_and_save_code(generated, "generated_blog_api.py")

    elif mode == "complex":
        # 복잡한 코드 생성 (adaptive thinking 활용)
        generated = generate_api_code(EXAMPLE_COMPLEX, use_thinking=True)
        extract_and_save_code(generated, "generated_order_api.py")

    elif mode == "interactive":
        # 다중 턴 대화로 코드 개선
        custom_requirements = """
        사용자 관리 API (username, email, password 필드)
        CRUD 기능 + 비밀번호 변경 엔드포인트 포함
        """
        interactive_refinement(custom_requirements)

    else:
        print("사용법: python main.py [simple|complex|interactive]")
