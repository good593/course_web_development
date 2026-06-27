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
# 생성형 AI를 활용한 API 코드 자동 생성

---
## 학습 목표

- Ollama를 설치하고 로컬 LLM `gemma4`를 실행할 수 있다
- Python에서 Ollama Chat API를 호출할 수 있다
- 스트리밍 방식으로 긴 코드 생성 결과를 실시간으로 수신할 수 있다
- gemma4 thinking 모드의 사용 방법과 주의점을 설명할 수 있다
- FastAPI/Pydantic 코드를 자동 생성하는 프롬프트를 작성할 수 있다

---
## [Ollama란?](https://ollama.com/)
- Ollama는 대형 언어 모델(LLM)을 내 PC에서 쉽게 실행할 수 있게 해주는 오픈소스 도구입니다.
- 쉽게 말하면, ChatGPT 같은 AI 모델을 클라우드 대신 로컬 컴퓨터(Mac/Windows/Linux) 에서 돌릴 수 있게 해줍니다.

---
| 항목               | Ollama                        | ChatGPT                        |
| ---------------- | ----------------------------- | ------------------------------ |
| **실행 방식**        | 로컬 PC에서 직접 실행                 | OpenAI 클라우드 서버에서 실행            |
| **인터넷 연결**       | 모델 다운로드 후 오프라인 사용 가능          | 인터넷 연결 필수                      |
| **개인정보 보호**      | 데이터가 외부 서버로 전송되지 않음           | 대화 내용이 서버를 통해 처리됨              |
| **초기 구축 난이도**    | 설치 및 모델 선택 필요                 | 회원가입 후 바로 사용 가능                |
| **사용 편의성**       | 개발자 친화적, 터미널 기반               | 일반 사용자 친화적, UI 제공              |
| **보안 요구가 높은 환경** | 사내망·폐쇄망 환경에 적합                | 외부 네트워크 사용 정책 검토 필요            |
| **추천 사용자**       | 개발자, 연구자, 보안이 중요한 조직          | 일반 사용자, 업무 생산성 중심 사용자          |


---
## 1. 생성형 AI 코드 생성이란?

Ollama에서 실행하는 로컬 대형 언어 모델(LLM)은 자연어 설명을 받아 **완성된 코드 초안**을 생성할 수 있습니다.

---
```
개발자: "사용자 등록/조회/삭제 REST API를 FastAPI와 Pydantic으로 만들어줘"
    |
    v
Ollama + gemma4
    |
    v
완성된 FastAPI 코드 (main.py, models.py, schemas.py ...)
```

**활용 시나리오:**

- 반복적인 CRUD 엔드포인트 초안 생성
- Pydantic 모델 자동 설계
- 테스트 코드 골격 생성
- 기존 코드 리팩터링 제안

---
## 2. 환경 준비

---
### Ollama 설치

1. [ollama.com](https://ollama.com)에서 Ollama를 설치합니다.
2. 터미널에서 Ollama가 동작하는지 확인합니다.

```bash
ollama --version
```

---
### [gemma4 모델 내려받기](https://ollama.com/library/gemma4)

```bash
ollama pull gemma4:e4b
```

또는 처음 실행과 동시에 내려받을 수 있습니다.

```bash
ollama run gemma4:e4b
```

> `gemma4:e4b`는 텍스트와 이미지 입력을 지원하는 Ollama 모델입니다. 기본 모델 외에도 `gemma4:e2b`, `gemma4:12b`, `gemma4:26b`, `gemma4:31b` 같은 변형을 선택할 수 있습니다.

---
### Python 패키지 설치

이 폴더는 `uv` 프로젝트이므로 먼저 프로젝트 환경을 동기화합니다.

```bash
uv sync
```

`uv`를 사용하지 않는 경우에는 필요한 패키지를 직접 설치할 수 있습니다.

```bash
pip install ollama fastapi "uvicorn[standard]"
```

---
### 예제 실행

CLI 예제를 실행할 때는 다음 명령을 사용합니다.

```bash
uv run python main.py simple
```

FastAPI 서버로 실행할 때는 다음 명령을 사용합니다.

```bash
uv run uvicorn main:app --reload --port 8001
```

---
## 3. 기본 API 호출

```python
from ollama import chat

response = chat(
    model="gemma4",
    messages=[
        {"role": "user", "content": "FastAPI로 Hello World 엔드포인트를 만드는 코드를 작성해줘."}
    ],
    options={
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64,
        "num_predict": 1024,
    },
)

print(response.message.content)
```

---
### 응답 구조

> Ollama Python 패키지는 응답을 객체처럼 읽을 수 있습니다.

```python
response.model                 # 사용된 모델
response.message.role          # "assistant"
response.message.content       # 실제 텍스트
response.done                  # 생성 완료 여부
response.prompt_eval_count     # 입력 토큰 수 추정
response.eval_count            # 출력 토큰 수 추정
response.total_duration        # 전체 처리 시간(ns)
```

패키지 버전에 따라 일부 통계 필드는 없을 수 있습니다. 수업 코드에서는 `getattr()`로 안전하게 읽습니다.

---
## 4. 스트리밍 - 실시간 출력

코드 생성처럼 긴 응답은 스트리밍으로 수신하면 사용자가 결과를 기다리는 동안 진행 상황을 바로 확인할 수 있습니다.

```python
from ollama import chat

stream = chat(
    model="gemma4",
    messages=[{"role": "user", "content": prompt}],
    stream=True,
    ...
)

for chunk in stream:
    text = chunk.message.content or ""
    print(text, end="", flush=True)
```

---
## 5. gemma4 thinking 모드 활용

복잡한 아키텍처 설계나 까다로운 검증 로직처럼 깊은 추론이 필요한 작업에는 gemma4의 thinking 모드를 사용할 수 있습니다.

thinking 모드는 `system` 프롬프트 맨 앞에 `<|think|>` 토큰을 넣어 켭니다. 끄고 싶으면 이 토큰을 제거합니다.

---
```python
from ollama import chat

SYSTEM_PROMPT = """<|think|>
당신은 FastAPI 전문가입니다.
복잡한 요구사항을 단계적으로 검토한 뒤 실행 가능한 코드를 작성하세요.
"""

stream = chat(
    model="gemma4",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ],
)

```

> 다중 턴 대화에서는 이전 assistant 응답을 다시 messages에 넣을 때 thinking 내용을 제외하고 최종 답변만 저장하는 것이 좋습니다.

---
## 6. 프롬프트 엔지니어링 - 좋은 코드를 얻는 법

---
### 나쁜 프롬프트 vs 좋은 프롬프트

**나쁜 예:**

```
FastAPI 코드 만들어줘
```

---
**좋은 예:**

```
FastAPI와 Pydantic v2를 사용해서 상품 관리 API를 만들어줘.

[요구사항]
- POST /products: 상품 생성
- GET /products: 상품 목록 조회 (페이지네이션: page, size 쿼리 파라미터)
- GET /products/{product_id}: 특정 상품 조회
- PATCH /products/{product_id}: 상품 부분 수정
- DELETE /products/{product_id}: 상품 삭제

[데이터 모델]
- Product: id(int), name(str, 2~100자), price(int, 1원 이상), stock(int, 0 이상), category(str)
- 입력 스키마(ProductCreate)와 응답 스키마(ProductResponse) 분리

[검증]
- 상품명 중복 불허 (409)
- 재고보다 많은 수량 주문 불허 (400)
- 존재하지 않는 상품 404 반환

[기타]
- 인메모리 dict 사용
- 모든 엔드포인트에 적절한 HTTP 상태 코드
- 한국어 주석 포함
```

---
### 프롬프트 체크리스트

- [ ] 사용할 프레임워크/라이브러리 명시
- [ ] 엔드포인트 목록과 HTTP 메서드 명시
- [ ] 데이터 모델 필드와 제약 조건 명시
- [ ] 에러 처리 요구사항 명시
- [ ] 코드 스타일/언어 명시 (한국어 주석, 타입 힌트 등)
- [ ] 사용 금지 항목 명시 (DB 없이 인메모리만 등)

---
## 7. FastAPI 코드 자동 생성기 만들기

```python
def generate_api_code(requirements: str) -> str:
    """자연어 요구사항을 받아 FastAPI 코드를 생성합니다."""
    
    stream = chat(
        ...
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"다음 API를 구현해줘:\n\n{requirements}"},
        ],
    )

    result = []
    for chunk in stream:
        text = chunk.message.content or ""
        print(text, end="", flush=True)
        result.append(text)

    return "".join(result)
```

---
## 8. 다중 턴 대화로 반복 개선

```python
SYSTEM_PROMPT = "당신은 FastAPI 코드 생성 도우미입니다. 사용자의 피드백을 반영해 코드를 개선합니다."
conversation = []


def chat_with_model(user_message: str) -> str:
    conversation.append({"role": "user", "content": user_message})

    stream = chat(
        ...
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation,
        ],
    )

    ...


# 1턴: 초안 생성
chat_with_model("사용자 CRUD API를 FastAPI로 만들어줘.")

# 2턴: 개선 요청
chat_with_model("비밀번호 해싱 기능을 추가하고, 응답에서 비밀번호 필드를 제거해줘.")
```

---
## 9. 로컬 실행 관리

Ollama는 로컬에서 모델을 실행하므로 API 호출 비용 대신 PC 자원 사용량이 중요합니다.

---
### 실행 전 확인

```bash
ollama list
ollama ps
```

- `ollama list`: 내려받은 모델 목록 확인
- `ollama ps`: 현재 메모리에 올라간 모델 확인

---
### 모델별 특성

| 모델 | 용도 | 특징 |
|------|------|------|
| `gemma4` | 기본 실습 | 기본 태그, 텍스트/이미지 입력 지원 |
| `gemma4:e2b` | 가벼운 로컬 실습 | 작은 edge 모델, 128K 컨텍스트 |
| `gemma4:e4b` | 균형형 로컬 실습 | 기본 `latest`와 같은 계열, 128K 컨텍스트 |
| `gemma4:12b` | 코드 생성 품질 강화 | 256K 컨텍스트 |
| `gemma4:26b` | 복잡한 설계/추론 | MoE 모델, 256K 컨텍스트 |
| `gemma4:31b` | 고성능 워크스테이션 | dense 모델, 256K 컨텍스트 |

---
### 로컬 실행 통계 확인

비스트리밍 응답에서는 토큰 수와 처리 시간 같은 통계를 확인할 수 있습니다.

```python
from ollama import chat

response = chat(
    model="gemma4",
    messages=[{"role": "user", "content": "FastAPI 코드 생성 프롬프트 예시를 하나 만들어줘."}],
    options={
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64,
        "num_predict": 512,
    },
)

print(response.message.content)
print(f"입력 토큰 추정: {response.prompt_eval_count}")
print(f"출력 토큰 추정: {response.eval_count}")
print(f"총 소요 시간: {response.total_duration / 1_000_000_000:.2f}초")
```

---

## 핵심 정리

| 기능 | 코드 |
|------|------|
| 모델 내려받기 | `ollama pull gemma4` |
| 응답 텍스트 | `response.message.content` |
| 스트리밍 | `stream=True`, `chunk.message.content` |
| 샘플링 옵션 | `options={"temperature": 1.0, "top_p": 0.95, "top_k": 64}` |
| 시스템 프롬프트 | `{"role": "system", "content": SYSTEM_PROMPT}` |
| 다중 턴 대화 | `messages` 리스트에 이전 대화 포함 |
| 실행 통계 | `response.eval_count`, `response.total_duration` |

