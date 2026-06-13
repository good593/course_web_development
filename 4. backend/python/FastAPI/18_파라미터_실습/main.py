"""
18교시 실습: 제어 파라미터 (temperature, top_p, top_k, max_output_tokens)

실행: python main.py
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.5-flash"


def generate(prompt: str, **kwargs) -> str:
    """파라미터를 넘겨 텍스트를 생성한다."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(**kwargs),
    )
    return response.text


# ── 1. temperature 비교 ────────────────────────────────────────────────

def compare_temperature():
    print("\n[1] temperature 비교 - 같은 질문, 다른 창의성")
    print("=" * 60)

    prompt = "새로운 카페 이름을 하나 제안해주세요. 이름만 답해주세요."
    temps = [0.0, 0.5, 1.0, 1.5, 2.0]

    for temp in temps:
        # 같은 온도로 3번 반복해 일관성 확인
        results = []
        for _ in range(3):
            text = generate(prompt, temperature=temp, max_output_tokens=30)
            results.append(text.strip()[:20])
        print(f"  temperature={temp:.1f}: {' | '.join(results)}")


# ── 2. max_output_tokens 비교 ──────────────────────────────────────────

def compare_max_tokens():
    print("\n[2] max_output_tokens - 응답 길이 제어")
    print("=" * 60)

    prompt = "Python의 주요 특징을 설명해주세요."
    token_limits = [30, 100, 300]

    for limit in token_limits:
        text = generate(prompt, max_output_tokens=limit, temperature=0.3)
        finish = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=limit,
                temperature=0.3,
            ),
        ).candidates[0].finish_reason

        print(f"\n  max_output_tokens={limit} (finish_reason={finish}):")
        print(f"  {text[:120]}{'...' if len(text) > 120 else ''}")


# ── 3. top_p 비교 ─────────────────────────────────────────────────────

def compare_top_p():
    print("\n[3] top_p 비교 - 어휘 다양성")
    print("=" * 60)

    prompt = "하늘을 묘사하는 형용사 하나만 답해주세요."
    top_p_values = [0.5, 0.9, 1.0]

    for top_p in top_p_values:
        results = set()
        for _ in range(5):
            text = generate(
                prompt,
                temperature=1.0,
                top_p=top_p,
                max_output_tokens=10,
            )
            results.add(text.strip())
        print(f"  top_p={top_p}: 5회 중 {len(results)}가지 다른 답변 -> {results}")


# ── 4. stop_sequences 실습 ─────────────────────────────────────────────

def stop_sequences_demo():
    print("\n[4] stop_sequences - 특정 문자열에서 중단")
    print("=" * 60)

    prompt = (
        "Python 학습 단계를 번호 목록으로 나열해줘. "
        "각 항목 뒤에 마침표를 붙여줘. "
        "5개 작성 후 '---끝---' 을 출력해."
    )

    # stop_sequences 없이
    text_no_stop = generate(prompt, temperature=0.3, max_output_tokens=300)
    print(f"  stop 없음 (일부): {text_no_stop[:150]}...")

    # stop_sequences 있음
    text_with_stop = generate(
        prompt,
        temperature=0.3,
        max_output_tokens=300,
        stop_sequences=["---끝---"],
    )
    print(f"\n  stop 있음: {text_with_stop[:150]}")


# ── 5. 용도별 최적 파라미터 레시피 ────────────────────────────────────

RECIPES = {
    "사실_기반_QA": {
        "temperature": 0.1,
        "top_p": 0.8,
        "max_output_tokens": 500,
    },
    "자연스러운_대화": {
        "temperature": 0.8,
        "top_p": 0.95,
        "max_output_tokens": 800,
    },
    "창의적_글쓰기": {
        "temperature": 1.4,
        "top_p": 0.99,
        "max_output_tokens": 1000,
    },
    "코드_생성": {
        "temperature": 0.3,
        "top_p": 0.9,
        "max_output_tokens": 1024,
    },
}


def recipe_demo():
    print("\n[5] 용도별 레시피 비교")
    print("=" * 60)

    prompt = "파이썬으로 간단한 계산기를 만드는 방법을 설명해주세요."

    for name, params in RECIPES.items():
        text = generate(prompt, **params)
        print(f"\n  [{name}] (temp={params['temperature']})")
        print(f"  {text[:120]}...")


# ── 6. 파라미터 튜닝 실험 ──────────────────────────────────────────────

def parameter_tuning_experiment():
    print("\n[6] 파라미터 튜닝 실험 - 감성 문장 생성")
    print("=" * 60)

    prompt = "봄날 오후의 느낌을 한 문장으로 표현해주세요."
    experiments = [
        {"temperature": 0.1, "top_p": 0.7},
        {"temperature": 0.7, "top_p": 0.9},
        {"temperature": 1.2, "top_p": 0.95},
        {"temperature": 1.8, "top_p": 0.99},
    ]

    for params in experiments:
        text = generate(prompt, max_output_tokens=80, **params)
        print(f"  temp={params['temperature']}, top_p={params['top_p']}: {text.strip()}")


# ── 메인 ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  18교시: 제어 파라미터 실습")
    print("=" * 60)

    compare_temperature()
    compare_max_tokens()
    compare_top_p()
    stop_sequences_demo()
    recipe_demo()
    parameter_tuning_experiment()

    print("\n" + "=" * 60)
    print("  다음 시간: 싱글턴 vs 멀티턴 대화 구현!")
    print("=" * 60)


if __name__ == "__main__":
    main()
