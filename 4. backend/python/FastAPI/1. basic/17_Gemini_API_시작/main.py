"""
17교시 실습: Gemini API 키 발급 및 SDK 기본 호출

사전 준비:
  1. aistudio.google.com 에서 API 키 발급
  2. .env 파일에 GEMINI_API_KEY=AIza... 저장
  3. pip install google-genai python-dotenv

실행: python main.py
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.5-flash"


# ── 1. 가장 간단한 호출 ─────────────────────────────────────────────────

def hello_gemini():
    """첫 번째 Gemini API 호출."""
    print("\n[1] 첫 번째 API 호출")
    print("-" * 40)

    response = client.models.generate_content(
        model=MODEL,
        contents="안녕하세요! 한 문장으로 자기소개를 해주세요.",
    )
    print(response.text)


# ── 2. 응답 구조 탐색 ───────────────────────────────────────────────────

def explore_response():
    """응답 객체의 구조를 분석한다."""
    print("\n[2] 응답 구조 분석")
    print("-" * 40)

    response = client.models.generate_content(
        model=MODEL,
        contents="Python의 장점 3가지를 간단히 나열해주세요.",
    )

    print(f"응답 텍스트:\n{response.text}")
    print()

    usage = response.usage_metadata
    print(f"입력 토큰:  {usage.prompt_token_count}")
    print(f"출력 토큰:  {usage.candidates_token_count}")
    print(f"총 토큰:    {usage.total_token_count}")

    candidate = response.candidates[0]
    print(f"중단 이유:  {candidate.finish_reason}")


# ── 3. 시스템 지시문 ───────────────────────────────────────────────────

def system_instruction_demo():
    """시스템 지시문으로 모델 역할을 지정한다."""
    print("\n[3] 시스템 지시문 실습")
    print("-" * 40)

    roles = [
        ("친절한 한국어 선생님", "영어 문장 'The quick brown fox' 를 설명해주세요."),
        ("엄격한 코드 리뷰어", "아래 코드를 검토해주세요:\ndef add(a, b):\n  return a+b"),
        ("5살 아이에게 설명하는 과학자", "블랙홀이 뭔가요?"),
    ]

    for role, question in roles:
        print(f"\n역할: {role}")
        print(f"질문: {question[:40]}...")
        response = client.models.generate_content(
            model=MODEL,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=f"당신은 {role}입니다. 항상 그 역할에 맞게 답변하세요.",
                max_output_tokens=200,
            ),
        )
        print(f"답변: {response.text[:200]}")


# ── 4. 토큰 사전 카운팅 ─────────────────────────────────────────────────

def token_counting_demo():
    """API 호출 전에 토큰 수를 미리 확인한다."""
    print("\n[4] 토큰 카운팅")
    print("-" * 40)

    texts = [
        "Hello",
        "안녕하세요",
        "FastAPI는 Python 기반의 고성능 웹 프레임워크로, 자동 문서화와 타입 안전성을 제공합니다.",
        "Explain the difference between synchronous and asynchronous programming in Python with examples.",
    ]

    for text in texts:
        token_response = client.models.count_tokens(
            model=MODEL,
            contents=text,
        )
        print(f"  {token_response.total_tokens:4d} tokens | {text[:60]}")


# ── 5. 에러 처리 실습 ──────────────────────────────────────────────────

def error_handling_demo():
    """다양한 에러 상황과 처리 방법을 보여준다."""
    print("\n[5] 에러 처리")
    print("-" * 40)

    test_cases = [
        ("정상 요청", MODEL, "짧게 답해주세요: 하늘은 왜 파란가요?"),
        ("잘못된 모델명", "gemini-nonexistent-model", "안녕"),
    ]

    for label, model, content in test_cases:
        print(f"\n  케이스: {label}")
        try:
            response = client.models.generate_content(
                model=model,
                contents=content,
            )
            print(f"  성공: {response.text[:80]}")

        except errors.APIError as e:
            print(f"  APIError [{e.status_code}]: {e.message[:100]}")

        except Exception as e:
            print(f"  예외: {type(e).__name__}: {str(e)[:100]}")


# ── 6. 모델 목록 조회 ──────────────────────────────────────────────────

def list_models():
    """사용 가능한 Gemini 모델 목록을 조회한다."""
    print("\n[6] 사용 가능한 모델 목록")
    print("-" * 40)

    models = list(client.models.list())
    gemini_models = [m for m in models if "gemini" in m.name.lower()]

    for m in gemini_models[:10]:
        name = m.name.split("/")[-1] if "/" in m.name else m.name
        print(f"  {name}")

    if len(gemini_models) > 10:
        print(f"  ... 외 {len(gemini_models) - 10}개")


# ── 메인 ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  17교시: Gemini API 기본 호출 실습")
    print("=" * 60)

    hello_gemini()
    explore_response()
    system_instruction_demo()
    token_counting_demo()
    error_handling_demo()
    list_models()

    print("\n" + "=" * 60)
    print("  다음 시간: 제어 파라미터 실습 (temperature, top-p 등)")
    print("=" * 60)


if __name__ == "__main__":
    main()
