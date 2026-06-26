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
# 생성형 AI를 활용한 API 문서 자동화

---
## 학습 목표

- FastAPI의 openapi.json을 Groq API에 전달해 마크다운 문서를 자동 생성할 수 있다
- Groq로 Postman Collection JSON을 자동 생성할 수 있다
- API 코드를 분석해 README와 사용 가이드를 자동화할 수 있다
- 문서 자동화 워크플로우를 실무 프로젝트에 적용할 수 있다

---
## [Groq](https://console.groq.com/home)
> Groq 는 자체 개발한 LPU(Language Processing Unit) 를 기반으로 초고속 AI 추론 서비스를 제공하는 회사이다.

---
| 항목 | 설명 |
|---|---|
| Groq | AI 추론(Inference)에 특화된 반도체와 클라우드 서비스를 제공하는 기업 |
| 핵심 기술 | LPU(Language Processing Unit)라는 자체 AI 가속기 칩 |
| 특징 | 매우 빠른 응답 속도와 낮은 지연 시간(Low Latency) |
| 주요 용도 | LLM 추론 서비스, 챗봇, 실시간 AI 애플리케이션 |
| 장점 | 높은 처리 속도, 간편한 API 제공, 오픈소스 모델 지원 |
| 단점 | OpenAI처럼 자체 거대 언어 모델을 제공하는 것은 아님 |

---
| 항목 | Groq | Ollama |
|---|---|---|
| 종류 | 클라우드 기반 AI 추론 서비스 | 로컬 LLM 실행 도구 |
| 실행 위치 | Groq 서버 | 내 PC/Mac |
| 인터넷 필요 여부 | 필요 | 불필요 (모델 다운로드 후 오프라인 가능) |
| 속도 | 매우 빠름 (LPU 기반) | PC 사양에 따라 다름 |
| 비용 | 사용량 기반 과금 (일부 무료 제공) | 무료 (하드웨어 비용 제외) |
| 개인정보 | 외부 서버로 요청 전송 | 로컬에서 처리되어 데이터 유출 위험 낮음 |
| 설치 난이도 | API Key 발급 후 바로 사용 | Ollama 설치 및 모델 다운로드 필요 |

---
## 1. API 문서 자동화가 필요한 이유

| 문제 | 설명 |
|------|------|
| 문서 누락 | 개발 속도에 문서화가 따라가지 못함 |
| 문서 불일치 | 코드는 바뀌었는데 문서는 구버전 그대로 |
| 작성 부담 | 엔드포인트 20개 → 예시·설명 수동 작성 시간 과다 |
| 팀 규칙 불일치 | 작성자마다 문서 스타일이 다름 |

생성형 AI를 활용하면 **코드 → 문서**를 자동화해 항상 최신 상태를 유지할 수 있습니다.

---
## 2. 자동화 흐름

```
FastAPI 서버
     │
     ▼ GET /openapi.json
OpenAPI 스펙 (JSON)
     │
     ▼
Groq API
     │
     ├──► 마크다운 API 문서
     ├──► Postman Collection JSON
     └──► README.md
```

---
## 3. openapi.json 읽기

FastAPI 서버가 실행 중일 때 스펙을 가져오는 두 가지 방법입니다.

### 방법 1 — HTTP 요청으로 가져오기 (서버 실행 중)

```python
import httpx

response = httpx.get("http://localhost:8001/openapi.json")
openapi_spec = response.json()
```

---
### 방법 2 — FastAPI 앱 객체에서 직접 추출 (서버 없이)

```python
import json
from main import app  # FastAPI 앱 임포트

openapi_spec = app.openapi()
spec_text = json.dumps(openapi_spec, ensure_ascii=False, indent=2)
```

---
## 4. 마크다운 API 문서 자동 생성

```python
import json

import httpx
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # .env 파일에서 GROQ_API_KEY 로드
client = Groq()

MODEL = "openai/gpt-oss-120b"

...
```

---
## 5. Postman Collection 자동 생성

````python
...

def save_collection(collection_json: str, filename: str = "collection.json"):
    # JSON 유효성 검사 후 저장
    parsed = json.loads(collection_json)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    print(f"\nCollection이 '{filename}'에 저장되었습니다.")
    print("Postman → Import → 파일 선택으로 가져올 수 있습니다.")
````

---
## 6. README 자동 생성

```python
def generate_readme(spec: dict, project_description: str = "") -> str:
    spec_text = json.dumps(spec, ensure_ascii=False, indent=2)

    prompt = f"""다음 OpenAPI 스펙을 기반으로 GitHub README.md를 작성해줘.

...
"""
    return stream_groq(prompt, max_tokens=4096, reasoning_effort="medium")
```

---
## 7. 증분 문서화 — 변경된 엔드포인트만 업데이트

코드가 바뀔 때마다 전체 문서를 재생성하면 비효율적입니다.  
이전 스펙과 비교해 **변경된 부분만** 업데이트하는 방식입니다.

```python
def update_docs_for_changes(changes: list[dict]) -> str:
    if not changes:
        print("변경된 엔드포인트가 없습니다.")
        return ""

    changes_text = json.dumps(changes, ensure_ascii=False, indent=2)
    prompt = f"""다음 변경된 API 엔드포인트에 대한 문서를 마크다운으로 작성해줘.
각 엔드포인트의 설명, curl 예시, 응답 예시를 포함해줘.

[변경사항]
{changes_text}
"""
    return stream_groq(prompt, max_tokens=4096, reasoning_effort="medium")
```

---

## 8. 전체 자동화 파이프라인

```python
def run_pipeline(server_url: str = "http://localhost:8001"):
    print("=" * 60)
    print("API 문서 자동화 파이프라인 시작")
    print("=" * 60)

    # 1단계: 스펙 수집
    print("\n[1/4] OpenAPI 스펙 수집 중...")
    spec = fetch_openapi_spec(server_url)
    print(f"  엔드포인트 수: {sum(len(v) for v in spec.get('paths', {}).values())}")

    # 2단계: 마크다운 API 문서 생성
    print("\n[2/4] 마크다운 API 문서 생성 중...")
    docs = generate_api_docs(spec)
    save_docs(docs, "output/API_DOCS.md")

    ...
```

---
## 9. 실습 순서
- fastapi server 실행 
```bash
uvicorn api_server:app --reload --port 8001
```

---
- 생성형 AI를 활용한 API 문서 자동화 실행

```bash
# 전체 파이프라인
python main.py pipeline

# openapi.json 전체 URL을 직접 넘겨도 동작
python main.py pipeline http://localhost:8001/openapi.json

# 마크다운 문서만
python main.py docs

# Postman Collection만
python main.py collection

# README만
python main.py readme
```

4. `output/` 폴더에서 생성된 파일 확인
5. `output/collection.json` → Postman Import

---
## 10. 모델과 토큰 사용량 확인

예제에서는 문서 생성에 `openai/gpt-oss-120b` 모델을 사용합니다. 긴 OpenAPI 스펙을 처리해야 하므로 응답 토큰 한도를 충분히 크게 잡고, 복잡한 문서 생성에는 `reasoning_effort="medium"`을 사용합니다.

Groq 무료/온디맨드 티어에서는 모델별 TPM(Token Per Minute) 제한이 낮을 수 있습니다. 전체 OpenAPI JSON을 그대로 보내면 요청이 거절될 수 있으므로, 실습 코드에서는 프롬프트 전송 전에 스펙을 핵심 필드만 남긴 compact JSON으로 줄이고 `max_completion_tokens`도 제한합니다.

스트리밍 응답은 `stream=True`로 활성화합니다. 현재 설치된 Groq SDK 1.4.0에서는 `stream_options` 인자를 사용하지 않습니다.

---
```python
stream = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "간단한 API 문서 템플릿을 만들어줘."}],
    max_completion_tokens=1024,
    reasoning_effort="medium",
    reasoning_format="hidden",
    stream=True,
)

usage = None
for chunk in stream:
    if getattr(chunk, "usage", None) is not None:
        usage = chunk.usage

    if chunk.choices:
        print(chunk.choices[0].delta.content or "", end="")

if usage:
    print(f"\n총 토큰: {usage.total_tokens}")
```

---
## 핵심 정리

| 기능 | 방법 |
|------|------|
| 스펙 수집 | `GET /openapi.json` → JSON |
| Groq 클라이언트 | `client = Groq()` |
| 마크다운 문서 | OpenAPI JSON → Groq → .md 파일 |
| Postman Collection | OpenAPI JSON → Groq → collection.json |
| README 생성 | OpenAPI JSON → Groq → README.md |
| 스트리밍 | `stream=True`, `chunk.choices[0].delta.content` |
| 추론 강도 | `reasoning_effort` 값: `low`, `medium`, `high` |
| 파이프라인 | 스펙 수집 → 문서 → Collection → README 순 실행 |

