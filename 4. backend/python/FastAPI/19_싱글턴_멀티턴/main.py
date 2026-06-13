"""
19교시 실습: 싱글턴 vs 멀티턴 호출 차이

실행: python main.py
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.5-flash"


# ── 1. 싱글턴 — 대화를 기억하지 못함 ─────────────────────────────────

def demo_single_turn():
    print("\n[1] 싱글턴 호출 - 문맥 없음")
    print("=" * 60)

    questions = [
        "파이썬이 뭐야? 한 문장으로 답해줘.",
        "방금 말한 것보다 더 쉽게 설명해줘.",     # '방금 말한 것' = 모름
        "예시 코드도 짧게 줘.",                   # 무슨 코드인지 모름
    ]

    for i, q in enumerate(questions, 1):
        response = client.models.generate_content(
            model=MODEL,
            contents=q,
            config=types.GenerateContentConfig(max_output_tokens=150),
        )
        print(f"\n  Q{i}: {q}")
        print(f"  A{i}: {response.text.strip()[:120]}")

    print("\n  각 질문이 독립적 - '방금 말한 것'을 모름")


# ── 2. 멀티턴 — Chat 세션으로 대화 유지 ──────────────────────────────

def demo_multi_turn():
    print("\n[2] 멀티턴 호출 - 문맥 유지")
    print("=" * 60)

    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(max_output_tokens=200),
    )

    conversations = [
        "파이썬이 뭐야? 한 문장으로 답해줘.",
        "방금 말한 것보다 더 쉽게 설명해줘.",
        "예시 코드도 짧게 줘.",
        "그 코드에서 변수명을 바꾸면 어떻게 되?",
    ]

    for i, msg in enumerate(conversations, 1):
        response = chat.send_message(msg)
        print(f"\n  Q{i}: {msg}")
        print(f"  A{i}: {response.text.strip()[:150]}")

    # 대화 기록 확인
    print("\n  --- 전체 대화 기록 ---")
    for turn in chat.get_history():
        role = "나  " if turn.role == "user" else "AI  "
        text = turn.parts[0].text.strip()[:60]
        print(f"  [{role}]: {text}...")


# ── 3. 시스템 지시문 + 멀티턴 ─────────────────────────────────────────

def demo_system_instruction_chat():
    print("\n[3] 시스템 지시문 + 멀티턴 - 역할 고정 챗봇")
    print("=" * 60)

    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=(
                "당신은 '코딩 요정'입니다. "
                "항상 반말을 쓰고, 재미있게 설명하며, "
                "답변 끝에 반드시 이모지를 붙여요. "
                "대화 중 사용자 이름을 '개발자님'으로 불러요."
            ),
            max_output_tokens=200,
        ),
    )

    messages = [
        "안녕! 나는 파이썬을 배우고 싶어.",
        "리스트가 뭐야?",
        "딕셔너리랑 차이가 뭔데?",
    ]

    for msg in messages:
        response = chat.send_message(msg)
        print(f"\n  나: {msg}")
        print(f"  코딩 요정: {response.text.strip()[:180]}")


# ── 4. 수동 기록 관리 (직접 history 제어) ─────────────────────────────

def demo_manual_history():
    print("\n[4] 수동 기록 관리 - history 직접 제어")
    print("=" * 60)

    history: list[types.Content] = []

    def chat_turn(user_message: str) -> str:
        history.append(
            types.Content(role="user", parts=[types.Part(text=user_message)])
        )
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(max_output_tokens=150),
        )
        answer = response.text
        history.append(
            types.Content(role="model", parts=[types.Part(text=answer)])
        )
        return answer

    turns = [
        "제일 좋아하는 프로그래밍 언어를 골라줘.",
        "왜 그 언어를 골랐어?",
        "단점은 없어?",
    ]

    for msg in turns:
        answer = chat_turn(msg)
        print(f"\n  나: {msg}")
        print(f"  AI: {answer.strip()[:150]}")

    print(f"\n  현재 기록 길이: {len(history)} 메시지")
    print(f"  (user {len([h for h in history if h.role == 'user'])}개 + "
          f"model {len([h for h in history if h.role == 'model'])}개)")


# ── 5. 스트리밍 비교 ───────────────────────────────────────────────────

def demo_streaming():
    print("\n[5] 스트리밍 응답 - 실시간 출력")
    print("=" * 60)

    print("\n  [싱글턴 스트리밍]")
    print("  AI: ", end="", flush=True)
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents="파이썬의 장점을 50자 이내로 설명해줘.",
        config=types.GenerateContentConfig(max_output_tokens=100),
    ):
        print(chunk.text, end="", flush=True)
    print()

    print("\n  [멀티턴 스트리밍]")
    chat = client.chats.create(model=MODEL)

    # 첫 메시지 (문맥 설정)
    chat.send_message("자바스크립트에 대해 얘기해볼게.")

    print("  AI: ", end="", flush=True)
    for chunk in chat.send_message_stream(
        "방금 말한 언어의 단점을 50자 이내로 알려줘.",
    ):
        print(chunk.text, end="", flush=True)
    print()


# ── 6. 컨텍스트 축적 시각화 ───────────────────────────────────────────

def demo_context_growth():
    print("\n[6] 컨텍스트 성장 확인 - 대화할수록 토큰 증가")
    print("=" * 60)

    chat = client.chats.create(model=MODEL)
    short_questions = [
        "숫자 1을 영어로?",
        "숫자 2를 영어로?",
        "숫자 3을 영어로?",
        "숫자 4를 영어로?",
        "숫자 5를 영어로?",
    ]

    total_so_far = 0
    for i, q in enumerate(short_questions, 1):
        response = chat.send_message(q)
        usage = response.usage_metadata
        total_so_far = usage.total_token_count
        print(
            f"  대화 {i}회: 이번 입력={usage.prompt_token_count:4d}, "
            f"출력={usage.candidates_token_count:3d}, "
            f"누적 총={total_so_far:4d} 토큰"
        )

    print(f"\n  ↑ 대화가 쌓일수록 '입력 토큰'이 증가 (기록이 포함되므로)")


# ── 메인 ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  19교시: 싱글턴 vs 멀티턴 호출 실습")
    print("=" * 60)

    demo_single_turn()
    demo_multi_turn()
    demo_system_instruction_chat()
    demo_manual_history()
    demo_streaming()
    demo_context_growth()

    print("\n" + "=" * 60)
    print("  다음 시간: FastAPI + Gemini 연동!")
    print("=" * 60)


if __name__ == "__main__":
    main()
