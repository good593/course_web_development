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
# FastAPI + Gemini 연동

---
## 학습 목표

- FastAPI 엔드포인트에서 Gemini API를 비동기로 호출한다
- 사용자별 대화 세션을 서버에서 관리한다
- SSE(Server-Sent Events)로 스트리밍 응답을 구현한다
- 토큰 사용량 모니터링 엔드포인트를 추가한다

---
## 1. Gemini SDK 비동기 호출

---
### 동기 vs 비동기
> FastAPI는 기본적으로 비동기(async) 기반입니다. Gemini SDK는 동기와 비동기 두 방식을 모두 지원합니다.

```python
# 동기 (sync) — FastAPI에서 사용 시 이벤트 루프 블로킹 위험
response = client.models.generate_content(...)

# 비동기 (async) — FastAPI async 엔드포인트에서 권장
response = await client.aio.models.generate_content(...)
```

---
### 비동기 클라이언트

```python
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# client.aio 는 비동기 인터페이스
# - client.aio.models.generate_content()
# - client.aio.models.generate_content_stream()
# - client.aio.chats.create()
```

---
## 2. 단순 Q&A 엔드포인트

```python
app = FastAPI()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=req.question,
        config=types.GenerateContentConfig(
            temperature=req.temperature,
            max_output_tokens=req.max_tokens,
        ),
    )
    usage = response.usage_metadata
    return AskResponse(
        ...
    )

```

---
### 한국어 요청/응답 예제

```json
{
  "question": "FastAPI에서 비동기 처리가 필요한 이유를 쉽게 설명해줘.",
  "temperature": 0.7,
  "max_tokens": 500,
  "system_instruction": "너는 한국어로 친절하게 설명하는 백엔드 강사야."
}
```

```json
{
  "answer": "FastAPI에서 비동기 처리를 사용하면 오래 걸리는 API 호출 중에도 서버가 다른 요청을 계속 처리할 수 있습니다.",
  "input_tokens": 24,
  "output_tokens": 42,
  "total_tokens": 66
}
```

---
## 3. 대화 세션 관리
> Chat 세션(`client.chats`)은 비동기 버전(`client.aio.chats`)도 있습니다.

```python
from uuid import uuid4

# 메모리 내 세션 저장소
sessions: dict[str, object] = {}

def get_or_create_session(session_id: str) -> object:
    ...

@app.post("/chat/{session_id}")
async def chat(session_id: str, req: ChatRequest):
    chat_session = get_or_create_session(session_id)
    # 동기 Chat API를 asyncio.to_thread로 비동기화
    ...
```

---
### 세션 대화 요청 예제

```json
{
  "message": "방금 설명한 내용을 쇼핑몰 서비스 예시로 다시 설명해줘.",
  "temperature": 0.7,
  "max_tokens": 800
}
```

---
## 4. SSE 스트리밍 응답

긴 응답을 실시간으로 클라이언트에 전달합니다.

```python
from fastapi.responses import StreamingResponse
import asyncio

@app.post("/ask/stream")
async def ask_stream(req: AskRequest):
    async def event_generator():
        ...

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

---
### 클라이언트 측 (JavaScript)

```javascript
const source = new EventSource('/ask/stream');

source.onmessage = (event) => {
  if (event.data === '[DONE]') {
    source.close();
    return;
  }
  document.getElementById('output').textContent += event.data;
};
```

---
## 5. 전체 API 설계

```
POST /ask                  — 단순 질문/답변 (싱글턴)
POST /chat/sessions        — 새 대화 세션 생성
POST /chat/{session_id}    — 세션 내 대화 전송
GET  /chat/{session_id}/history  — 대화 기록 조회
DELETE /chat/{session_id}  — 세션 삭제
POST /ask/stream           — 스트리밍 단순 질문
POST /chat/{session_id}/stream   — 스트리밍 세션 대화
GET  /stats                — 토큰 사용량 통계
```

---
## 6. 토큰 사용량 추적

```python
from dataclasses import dataclass, field

@dataclass
class UsageStats:
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    ...

stats = UsageStats()

# 엔드포인트에서 사용
@app.post("/ask")
async def ask(req: AskRequest):
    response = await client.aio.models.generate_content(...)
    usage = response.usage_metadata
    stats.add(usage.prompt_token_count, usage.candidates_token_count)
    ...
```

---
## 7. 에러 처리 미들웨어

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from google.genai import errors

@app.exception_handler(errors.APIError)
async def gemini_error_handler(request: Request, exc: errors.APIError):
    status_map = {429: 429, 403: 401, 400: 400}
    status_code = status_map.get(exc.status_code, 502)
    return JSONResponse(
        status_code=status_code,
        content={"detail": f"Gemini API 에러: {exc.message}"},
    )
```

---
## 8. 세션 만료 처리

> 메모리 무한 증가를 막기 위해 오래된 세션을 정리합니다.

```python
import time

session_timestamps: dict[str, float] = {}
SESSION_TTL = 3600  # 1시간

def cleanup_old_sessions():
    now = time.time()
    expired = [
        sid for sid, ts in session_timestamps.items()
        if now - ts > SESSION_TTL
    ]
    for sid in expired:
        sessions.pop(sid, None)
        session_timestamps.pop(sid, None)
```

---
## 핵심 패턴 요약

| 기능 | 코드 패턴 |
|------|----------|
| 비동기 단일 호출 | `await client.aio.models.generate_content(...)` |
| 비동기 스트리밍 | `async for chunk in await client.aio.models.generate_content_stream(...)` |
| 동기 Chat 비동기화 | `await asyncio.to_thread(chat.send_message, msg)` |
| SSE 응답 | `StreamingResponse(generator(), media_type="text/event-stream")` |
| 에러 처리 | `@app.exception_handler(errors.APIError)` |
