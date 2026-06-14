---
style: |
  img {
    display: block;
    float: none;
    margin-left: auto;
    margin-right: auto;
  }
marp: true
paginate: true
---
# 파라미터 실습

---
## 학습 목표

- `temperature`, `top_p`, `top_k`, `max_output_tokens`의 역할을 이해한다
- 각 파라미터가 출력에 미치는 영향을 직접 실습한다
- 용도별 최적 파라미터 조합을 익힌다
- `stop_sequences`와 `candidate_count`를 활용할 수 있다
- API 요청 한도 오류를 이해하고 실습 코드를 안전하게 실행할 수 있다

---
## 1. 파라미터 전체 구조

```python
from google.genai import types

config = types.GenerateContentConfig(
    # 창의성 제어
    temperature=0.7,        # 0.0 ~ 2.0
    top_p=0.95,             # 0.0 ~ 1.0
    top_k=40,               # 정수

    # 길이 제어
    max_output_tokens=1000, # 최대 출력 토큰

    # 조기 종료
    stop_sequences=["---", "끝"],

    # 역할 지시
    system_instruction="당신은 친절한 도우미입니다.",
)
```

---
## 2. temperature — 창의성과 결정성

---
### 동작 원리

```
다음 토큰 후보 확률 분포:
"오늘 날씨가 ___"

temperature = 0.0  (결정적)
  맑다: 45% ████████████ ← 항상 선택
  흐리다: 30% ████████
  덥다: 15% ████

temperature = 1.0  (균형)
  맑다: 45%  ← 자주 선택
  흐리다: 30% ← 가끔 선택
  덥다: 15%  ← 드물게 선택

temperature = 2.0  (매우 무작위)
  거의 균등 분포 → 예측 불가능한 출력
```

---
### 권장 값

| 용도 | temperature | 이유 |
|------|-------------|------|
| 사실 기반 Q&A | 0.0 ~ 0.3 | 일관되고 정확한 답변 |
| 코드 생성 | 0.2 ~ 0.5 | 정확하되 약간의 다양성 |
| 일반 대화 | 0.7 ~ 1.0 | 자연스러운 변화 |
| 창작·브레인스토밍 | 1.0 ~ 1.5 | 다양한 아이디어 |
| 시/예술적 글쓰기 | 1.5 ~ 2.0 | 매우 창의적 |

---
## 3. top_p — 핵심 후보군 제한 (Nucleus Sampling)

상위 확률의 토큰들을 누적했을 때 `top_p`에 도달하는 후보군에서만 선택합니다.

```
토큰 확률:
  맑다:   45% ─┐
  흐리다: 30% ─┤ top_p=0.8 → 이 3개에서만 선택
  덥다:   15% ─┘  (합계 90% > 80%)
  춥다:    7%  ← 제외
  눈이 온다: 3% ← 제외
```

```python
# 보수적 생성 (높은 확률 토큰만)
config = types.GenerateContentConfig(top_p=0.7)

# 다양한 생성 (더 많은 후보 포함)
config = types.GenerateContentConfig(top_p=0.99)
```

> `temperature`와 함께 사용할 때는 주로 `top_p=0.95` 고정, `temperature`로 조절합니다.

---
## 4. top_k — 후보 수 직접 제한

상위 k개의 토큰만 후보로 허용합니다.

```python
# 상위 10개 토큰만 허용 (매우 보수적)
config = types.GenerateContentConfig(top_k=10)

# 상위 100개 토큰 허용 (다양성 증가)
config = types.GenerateContentConfig(top_k=100)
```

| top_k 값 | 특징 |
|----------|------|
| 1 | Greedy decoding (항상 최고 확률) |
| 10 ~ 40 | 균형 잡힌 기본값 |
| 100+ | 창의적, 예측 불가 |

---
## 5. max_output_tokens — 응답 길이 제한

```python
# 짧은 답변 강제 (분류, 키워드 추출)
config = types.GenerateContentConfig(max_output_tokens=50)

# 중간 길이 (일반 Q&A)
config = types.GenerateContentConfig(max_output_tokens=500)

# 긴 문서 생성
config = types.GenerateContentConfig(max_output_tokens=4096)
```

> 토큰 한도 도달 시 `finish_reason = "MAX_TOKENS"` — 응답이 잘릴 수 있음

---
## 6. stop_sequences — 특정 문자열에서 멈추기

```python
# 특정 마커가 나타나면 즉시 중단
config = types.GenerateContentConfig(
    stop_sequences=["STOP", "---", "\n\n"],
)
```

활용 예:
```
프롬프트: "1번 항목을 작성해줘. 끝나면 '---'를 출력해."
응답: "1번은 ... 입니다. ---"  ← '---' 직전에서 자름
```

---
## 7. 파라미터 조합 레시피

---
### 정확한 사실 답변용

```python
config = types.GenerateContentConfig(
    temperature=0.1,
    top_p=0.8,
    top_k=20,
    max_output_tokens=500,
)
```

---
### 자연스러운 챗봇용

```python
config = types.GenerateContentConfig(
    temperature=0.8,
    top_p=0.95,
    top_k=40,
    max_output_tokens=1000,
)
```

---
### 창의적 글쓰기용

```python
config = types.GenerateContentConfig(
    temperature=1.4,
    top_p=0.99,
    top_k=100,
    max_output_tokens=2000,
)
```

---
### 코드 생성용

```python
config = types.GenerateContentConfig(
    temperature=0.3,
    top_p=0.9,
    top_k=30,
    max_output_tokens=2048,
    stop_sequences=["```\n\n"],
)
```

---
## 8. finish_reason 해석

```python
response = client.models.generate_content(...)
reason = response.candidates[0].finish_reason

# STOP        — 정상 종료
# MAX_TOKENS  — 토큰 한도 도달 (응답 잘림)
# SAFETY      — 안전 필터 작동
# RECITATION  — 저작권 관련 중단
```

---
## 9. 요청 한도 오류와 실습 모드

Gemini API 무료 티어에서는 짧은 시간에 너무 많은 요청을 보내면 다음 오류가 발생할 수 있습니다.

```text
429 RESOURCE_EXHAUSTED
Quota exceeded for metric: generate_content_free_tier_requests
Please retry in 12s.
```

이 오류는 프롬프트나 파라미터 문법 오류가 아니라 **요청 횟수 제한**입니다.

---
### 왜 발생할까?

| 실습 | 요청 수 |
|------|---------|
| temperature 비교 | 5개 온도 × 3회 = 15회 |
| max_output_tokens 비교 | 3회 |
| top_p 비교 | 3개 값 × 5회 = 15회 |
| stop_sequences | 2회 |
| 레시피 비교 | 4회 |
| 튜닝 실험 | 4회 |
| 합계 | 43회 |

> 무료 티어의 분당 요청 제한보다 많으면 중간에 429 오류가 날 수 있습니다.

---
### 안전한 실행 방식

실습 코드는 기본 실행에서 API 요청을 5회로 줄여 quota 초과 가능성을 낮춥니다.

```powershell
python main.py
```

전체 비교를 보고 싶을 때만 `FULL_DEMO`를 켜서 실행합니다.

```powershell
$env:FULL_DEMO='1'
python main.py
```

---
### 429 오류 처리 패턴

```python
from google.genai import errors

try:
    response = client.models.generate_content(...)
except errors.APIError as error:
    if error.code == 429:
        print("요청 한도 초과: 잠시 기다린 뒤 다시 실행하세요.")
```

실무 코드에서는 `RetryInfo`의 대기 시간을 읽어 잠시 기다린 뒤 재시도하도록 만들 수 있습니다.

---
## 핵심 요약

| 파라미터 | 범위 | 높을수록 | 낮을수록 |
|----------|------|----------|----------|
| `temperature` | 0.0 ~ 2.0 | 창의적, 무작위 | 결정적, 일관성 |
| `top_p` | 0.0 ~ 1.0 | 다양한 어휘 사용 | 고확률 어휘만 사용 |
| `top_k` | 1 ~ | 다양성 증가 | 결정성 증가 |
| `max_output_tokens` | 1 ~ | 긴 답변 허용 | 짧은 답변 강제 |

---
## 실습 체크포인트

- `response.text`는 항상 문자열이 아닐 수 있다. 텍스트가 없으면 `None`일 수 있다
- `finish_reason`으로 응답이 왜 끝났는지 확인한다
- 429 오류는 API 요청 횟수 제한이다
- 반복 비교 실습은 기본 모드로 먼저 실행하고, 전체 실습은 필요할 때만 실행한다
