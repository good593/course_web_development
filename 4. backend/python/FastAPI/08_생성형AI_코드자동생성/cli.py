import sys

from ollama import ResponseError

from examples import EXAMPLE_COMPLEX, EXAMPLE_SIMPLE
from services.code_generator import (
    extract_and_save_code,
    generate_api_code,
    interactive_refinement,
    summarize_stats_example,
)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "simple"

    try:
        if mode == "simple":
            print(f"프롬프트 글자 수: {len(EXAMPLE_SIMPLE):,}\n")
            generated = generate_api_code(EXAMPLE_SIMPLE)
            extract_and_save_code(generated, "generated_blog_api.py")

        elif mode == "complex":
            generated = generate_api_code(EXAMPLE_COMPLEX, thinking=True)
            extract_and_save_code(generated, "generated_order_api.py")

        elif mode == "interactive":
            custom_requirements = """
            사용자 관리 API (username, email, password 필드)
            CRUD 기능 + 비밀번호 변경 엔드포인트 포함
            """
            interactive_refinement(custom_requirements)

        elif mode == "usage":
            summarize_stats_example(EXAMPLE_SIMPLE)

        else:
            print("사용법: python main.py [simple|complex|interactive|usage]")

    except ResponseError as error:
        print(f"\nOllama 호출 실패: {error}")
        print("Ollama가 실행 중인지, `ollama pull gemma4:e4b`를 먼저 실행했는지 확인하세요.")
        raise
