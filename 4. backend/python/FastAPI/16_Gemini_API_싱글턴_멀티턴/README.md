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
# 싱글턴 vs 멀티턴 호출 차이 실습

---
## 학습 목표

- 단일 호출(싱글턴)과 대화형 호출(멀티턴)의 차이를 이해한다
- `client.chats.create()`로 세션을 유지하는 대화를 구현한다
- 대화 기록이 컨텍스트 윈도우에 미치는 영향을 이해한다
- 시스템 지시문으로 챗봇의 역할을 고정하는 방법을 익힌다

---
## 1. 싱글턴 호출 vs 멀티턴 대화

---
### 싱글턴 (Single-Turn)

```
[나] "파이썬이 뭐야?"  ────────> [Gemini] "파이썬은 ..."
[나] "더 쉽게 설명해줘" ────────> [Gemini] "??? (무슨 얘기?)"  ← 기억 없음!
```
> 이전 대화를 기억하지 못합니다. 독립적인 요청/응답입니다.

---
### 멀티턴 (Multi-Turn)

```
[나] "파이썬이 뭐야?"   ──> [Gemini] "파이썬은 ..."
[나] "더 쉽게 설명해줘" ──> [Gemini] "쉽게 말하면, 파이썬은 ..."  ← 앞 대화 기억!
[나] "예시도 줘"        ──> [Gemini] "방금 말한 것처럼, 예를 들면 ..."
```
> 대화 기록이 누적되어 문맥을 유지합니다.

---
## 2. 싱글턴 구현

```python
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 매번 독립 호출
def ask_once(question: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=question,
    )
    return response.text
```

---

## 3. 멀티턴 구현 — Chat 세션

```python
# 세션 생성 (한 번만)
chat = client.chats.create(model="gemini-3.5-flash")

# 연속 메시지 전송
response1 = chat.send_message("파이썬이 뭐야?")
print(response1.text)

response2 = chat.send_message("더 쉽게 설명해줘")
print(response2.text)  # 파이썬 문맥 유지

response3 = chat.send_message("코드 예시도 보여줘")
print(response3.text)  # 여전히 파이썬 문맥
```

---
### 대화 기록 확인

```python
for turn in chat.get_history():
    role = turn.role   # "user" 또는 "model"
    text = turn.parts[0].text
    print(f"[{role}]: {text[:80]}")
```

---
## 4. 시스템 지시문으로 역할 고정

멀티턴에서 시스템 지시문으로 챗봇의 성격/역할을 유지합니다.

```python
chat = client.chats.create(
    model="gemini-3.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=(
            "당신은 친절한 Python 튜터입니다. "
            "항상 코드 예시와 함께 설명하고, "
            "초보자도 이해할 수 있도록 쉬운 언어를 사용하세요."
        ),
    ),
)
```

---
## 5. 컨텍스트 윈도우와 대화 기록

대화가 길어질수록 컨텍스트 윈도우를 더 많이 사용합니다.

```
대화 1회: [시스템 지시문] + [질문1] + [답변1]
대화 2회: [시스템 지시문] + [질문1] + [답변1] + [질문2] + [답변2]
...
대화 N회: 모든 기록이 누적 → 토큰 증가
```

---
### 대화 기록 관리 전략

```python
MAX_HISTORY_TURNS = 10

def trim_old_history(history: list) -> list:
    """오래된 대화를 제거해 컨텍스트를 관리한다."""
    if len(history) > MAX_HISTORY_TURNS * 2:
        # 최신 N턴만 유지
        return history[-MAX_HISTORY_TURNS * 2:]
    return history
```

---
## 6. 대화 기록을 직접 구성하는 멀티턴

Chat 세션 없이 기록을 직접 관리할 수도 있습니다.

```python
history = []

def chat_with_history(user_message: str) -> str:
    # 사용자 메시지 추가
    history.append({"role": "user", "parts": [{"text": user_message}]})

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=history,
    )

    answer = response.text
    # 모델 응답 추가
    history.append({"role": "model", "parts": [{"text": answer}]})
    return answer
```

---
## 7. 싱글턴 vs 멀티턴 비교표

| 항목 | 싱글턴 | 멀티턴 |
|------|--------|--------|
| 대화 기억 | X | O |
| 토큰 사용 | 일정 | 누적 증가 |
| 구현 복잡도 | 낮음 | 중간 |
| 용도 | 번역, 분류, 요약 | 챗봇, 튜터, 어시스턴트 |
| 세션 관리 | 불필요 | 사용자별 세션 필요 |
| 컨텍스트 한도 | 무관 | 주의 필요 |

---
## 8. 스트리밍 응답

응답이 생성되는 즉시 출력합니다 (긴 응답에 유리).

---
### 싱글턴 스트리밍

```python
for chunk in client.models.generate_content_stream(
    model="gemini-3.5-flash",
    contents="한국의 역사를 3000자로 설명해주세요.",
):
    print(chunk.text, end="", flush=True)
print()  # 줄바꿈
```

---
### 멀티턴 스트리밍

```python
chat = client.chats.create(model="gemini-3.5-flash")

for chunk in chat.send_message_stream("파이썬 개념을 자세히 설명해줘"):
    print(chunk.text, end="", flush=True)
print()
```

---
## 핵심 패턴 요약

```python
# 싱글턴 — 독립 호출
response = client.models.generate_content(model=MODEL, contents="질문")
print(response.text)

# 멀티턴 — 대화 세션
chat = client.chats.create(
    model=MODEL,
    config=types.GenerateContentConfig(system_instruction="역할 지시"),
)
response = chat.send_message("질문")
print(response.text)

# 스트리밍 (싱글턴)
for chunk in client.models.generate_content_stream(model=MODEL, contents="질문"):
    print(chunk.text, end="", flush=True)
```
