"""
16교시 실습: LLM API 개념 — 토큰 카운팅 & 과금 계산기

실행: python main.py
의존성 불필요 (표준 라이브러리만 사용)
"""

# ── 1. 간단한 토크나이저 시뮬레이션 ──────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """영어/한국어 혼합 텍스트의 토큰 수 근사 추정."""
    korean_chars = sum(1 for c in text if "가" <= c <= "힣")
    other_chars = len(text) - korean_chars
    # 한국어: 글자당 ~0.7 토큰, 영어: 단어당 ~0.75 토큰 (단어 ≈ 5글자)
    korean_tokens = korean_chars * 0.7
    other_tokens = other_chars / 4
    return max(1, int(korean_tokens + other_tokens))


# ── 2. 과금 계산기 ──────────────────────────────────────────────────────

PRICING = {
    "gemini-3.5-flash": {
        "input_per_1m":  1.50,   # USD, standard paid tier
        "output_per_1m": 9.00,
        "free_tier": True,
    },
    "gemini-3.1-flash-lite": {
        "input_per_1m":  0.25,   # USD, standard paid tier
        "output_per_1m": 1.50,
        "free_tier": True,
    },
    "claude-opus-4-8": {
        "input_per_1m":  5.00,
        "output_per_1m": 25.00,
        "free_tier": False,
    },
    "gpt-4o": {
        "input_per_1m":  2.50,
        "output_per_1m": 10.00,
        "free_tier": False,
    },
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> dict:
    if model not in PRICING:
        return {"error": f"알 수 없는 모델: {model}"}

    p = PRICING[model]
    input_cost  = (input_tokens  / 1_000_000) * p["input_per_1m"]
    output_cost = (output_tokens / 1_000_000) * p["output_per_1m"]
    total_cost  = input_cost + output_cost

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost_usd": round(input_cost, 8),
        "output_cost_usd": round(output_cost, 8),
        "total_cost_usd": round(total_cost, 8),
        "total_cost_krw": round(total_cost * 1350, 4),
    }


# ── 3. 컨텍스트 윈도우 모니터 ──────────────────────────────────────────

CONTEXT_WINDOWS = {
    "gemini-3.5-flash": 1_000_000,
    "claude-opus-4-8":  1_048_576,
    "gpt-4o":             128_000,
}


def context_usage(model: str, used_tokens: int) -> dict:
    limit = CONTEXT_WINDOWS.get(model, 128_000)
    pct = used_tokens / limit * 100
    remaining = limit - used_tokens
    bar_filled = int(pct / 5)
    bar = "#" * bar_filled + "-" * (20 - bar_filled)
    return {
        "model": model,
        "used": used_tokens,
        "limit": limit,
        "remaining": remaining,
        "percent": round(pct, 2),
        "bar": f"[{bar}] {pct:.1f}%",
    }


# ── 4. 월간 비용 시뮬레이터 ────────────────────────────────────────────

def monthly_cost_simulation(
    model: str,
    requests_per_day: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
) -> dict:
    p = PRICING.get(model, {})
    if not p:
        return {"error": f"알 수 없는 모델: {model}"}

    daily_reqs = requests_per_day
    monthly_reqs = daily_reqs * 30
    monthly_input  = monthly_reqs * avg_input_tokens
    monthly_output = monthly_reqs * avg_output_tokens

    cost = calculate_cost(model, monthly_input, monthly_output)

    return {
        "model": model,
        "requests_per_month": monthly_reqs,
        "total_input_tokens": monthly_input,
        "total_output_tokens": monthly_output,
        "estimated_monthly_cost_usd": cost["total_cost_usd"],
        "estimated_monthly_cost_krw": cost["total_cost_krw"],
        "pricing_note": "무료 티어와 할인은 제외한 표준 유료 단가 기준",
    }


# ── 메인 데모 ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  LLM API 개념 실습 - 토큰 카운팅 & 비용 계산기")
    print("=" * 60)

    # 1. 토큰 추정
    samples = [
        "Hello, how are you?",
        "안녕하세요, 오늘 날씨가 참 좋네요.",
        "FastAPI는 Python으로 REST API를 빠르게 개발할 수 있는 프레임워크입니다.",
        "Explain quantum computing in simple terms for a 10-year-old.",
    ]
    print("\n[1] 토큰 수 추정")
    for text in samples:
        tokens = estimate_tokens(text)
        print(f"  {tokens:4d} tokens | {text[:50]}")

    # 2. 단일 호출 비용
    print("\n[2] 단일 호출 비용 비교 (입력 200 토큰, 출력 500 토큰)")
    for model in PRICING:
        result = calculate_cost(model, 200, 500)
        usd = result["total_cost_usd"]
        krw = result["total_cost_krw"]
        free = "* 무료 티어 있음" if PRICING[model]["free_tier"] else ""
        print(f"  {model:<25} ${usd:.6f} (KRW {krw:.4f}) {free}")

    # 3. 컨텍스트 사용량
    print("\n[3] 컨텍스트 윈도우 사용량 (50,000 토큰 사용 중)")
    for model in CONTEXT_WINDOWS:
        info = context_usage(model, 50_000)
        print(f"  {model:<25} {info['bar']} (남은 토큰: {info['remaining']:,})")

    # 4. 월간 비용 시뮬레이션
    print("\n[4] 월간 비용 시뮬레이션 - 서비스 규모별")
    scenarios = [
        ("소규모 앱 (100 req/day)", 100, 300, 800),
        ("중규모 앱 (1,000 req/day)", 1000, 500, 1000),
        ("대규모 앱 (10,000 req/day)", 10000, 800, 1500),
    ]
    for label, rps, inp, out in scenarios:
        print(f"\n  {label} - Gemini 3.5 Flash 표준 유료 단가 기준")
        sim = monthly_cost_simulation("gemini-3.5-flash", rps, inp, out)
        print(f"    월간 요청:     {sim['requests_per_month']:,}회")
        print(f"    입력 토큰:     {sim['total_input_tokens']:,}개")
        print(f"    출력 토큰:     {sim['total_output_tokens']:,}개")
        print(f"    예상 월 비용:  ${sim['estimated_monthly_cost_usd']:.4f} (KRW {sim['estimated_monthly_cost_krw']:.0f})")

    print("\n" + "=" * 60)
    print("  다음 시간: Gemini API 키 발급 & 실제 API 호출!")
    print("=" * 60)


if __name__ == "__main__":
    main()
