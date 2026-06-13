# 환경 구성 & FastAPI 첫 실행

---

## 1. REST API란 무엇인가

### 클라이언트 / 서버 구조

```
[클라이언트]  ──── HTTP 요청 ────▶  [서버]
  브라우저                           FastAPI
  모바일앱     ◀─── HTTP 응답 ────   애플리케이션
  다른 서버
```

- **클라이언트** : 데이터를 요청하는 쪽 (브라우저, 앱, curl 등)
- **서버** : 요청을 받아 처리하고 응답을 돌려주는 쪽
- **API (Application Programming Interface)** : 클라이언트와 서버가 대화하는 약속된 방식

### REST란?

**RE**presentational **S**tate **T**ransfer — 리소스를 URI로 표현하고 HTTP 메서드로 행위를 나타내는 설계 원칙

```
# 좋은 REST URI 예시
GET  /users          → 유저 목록 조회
GET  /users/42       → ID 42번 유저 조회
POST /users          → 유저 생성
PUT  /users/42       → ID 42번 유저 수정
DELETE /users/42     → ID 42번 유저 삭제

# 나쁜 예시 (동사를 URI에 넣지 않는다)
GET  /getUsers       ❌
POST /createUser     ❌
GET  /deleteUser/42  ❌
```

---

## 2. 왜 FastAPI인가?

### 프레임워크 비교

| 항목 | Flask | Django REST | FastAPI |
|------|-------|-------------|---------|
| 학습 난이도 | 쉬움 | 어려움 | 쉬움 |
| 성능 (req/s) | 보통 | 보통 | 매우 빠름 |
| 타입 힌트 | 선택 | 선택 | 핵심 기능 |
| 자동 문서화 | 직접 설정 | 직접 설정 | **자동 (Swagger)** |
| 데이터 검증 | 직접 구현 | Serializer | **Pydantic 내장** |
| 비동기 지원 | 제한적 | 제한적 | **완전 지원** |

### FastAPI의 핵심 장점

```python
# 타입 힌트만 써도 자동으로:
# 1. 입력 데이터 검증
# 2. Swagger UI 문서 생성
# 3. IDE 자동완성 지원

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str        # 문자열 필수
    price: float     # 실수 필수
    in_stock: bool = True  # 기본값 있음

@app.post("/items")
def create_item(item: Item):   # ← 이것만으로 검증 + 문서화 완료
    return item
```

### ASGI / Uvicorn이란?

```
[HTTP 요청]
    ↓
[Uvicorn]  ← ASGI 서버 (비동기 요청 처리)
    ↓
[FastAPI]  ← ASGI 애플리케이션 (라우팅, 비즈니스 로직)
    ↓
[HTTP 응답]
```

- **WSGI** (Flask, Django) : 동기, 요청 하나씩 처리
- **ASGI** (FastAPI) : 비동기, 동시에 여러 요청 처리 가능
- **Uvicorn** : Python용 초고속 ASGI 서버

---

## 3. 실습 — 환경 구성

### 3-1. 프로젝트 준비

```bash
# 실습 폴더로 이동
cd 01_환경구성

# Python 버전 확인
python --version
```

이 예제는 `uv` 기반 프로젝트로 구성되어 있다.

| 파일 | 설명 |
|------|------|
| `.python-version` | 실습에 사용할 Python 버전 (`3.12`) |
| `pyproject.toml` | 프로젝트 메타데이터와 의존성 정의 |
| `uv.lock` | 재현 가능한 설치를 위한 잠금 파일 |

새 프로젝트에서 같은 환경을 직접 만들 경우:

```bash
uv init
uv python pin 3.12
```

### 3-2. 패키지 설치

```bash
# pyproject.toml과 uv.lock 기준으로 의존성 설치
uv sync

# 설치된 패키지 확인
uv pip list
```

현재 예제의 주요 의존성:

| 패키지 | 버전 |
|--------|------|
| `fastapi` | `0.115.12` |
| `uvicorn[standard]` | `0.34.3` |

새 프로젝트에서 직접 추가할 경우:

```bash
uv add "fastapi==0.115.12" "uvicorn[standard]==0.34.3"
```


### 3-3. Hello World 작성

`main.py`를 열고 아래 내용을 작성한다:

```python
from fastapi import FastAPI

app = FastAPI(
    title="My First API",
    description="FastAPI 입문 강의 실습",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"안녕하세요, {name}님!"}


@app.get("/info")
def get_info():
    return {
        "framework": "FastAPI",
        "language": "Python",
        "docs_url": "/docs",
    }
```

### 3-4. 서버 실행

```bash
uv run uvicorn main:app --reload --port 8001

# 출력 예시
# INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

| 옵션 | 설명 |
|------|------|
| `uv run` | 프로젝트 가상환경에서 명령 실행 |
| `main` | `main.py` 파일 |
| `app` | 파일 안의 FastAPI 인스턴스 변수명 |
| `--reload` | 파일 저장 시 자동 재시작 (개발용) |
