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
# CRUD 완성 — PATCH·오류 처리·집계 API

---
## 학습 목표

- `PUT`과 `PATCH`의 차이를 설명하고 PATCH를 올바르게 구현한다
- `model_dump(exclude_unset=True)`로 보내지 않은 필드를 필터링한다
- 집계 API(`/summary`)에서 대화 수와 메시지 수를 계산한다
- `Query` 파라미터로 메시지 조회 건수를 제한한다

---
## 1. PUT vs PATCH

| 메서드 | 의미 | 동작 방식 |
|--------|------|-----------|
| PUT | 전체 교체 | 보내지 않은 필드는 null/기본값으로 초기화 |
| PATCH | 부분 수정 | 보낸 필드만 수정, 나머지는 그대로 유지 |

---
### PUT 방식 — 문제점
> `display_name`만 바꾸고 싶어도 `username`을 함께 보내야 합니다.  
> 만약 `username`을 빠뜨리면 null로 초기화될 위험이 있습니다.
```python
# PUT /users/{id} — 전체를 보내야 함
{
  "username": "kim",
  "display_name": "김강사"  # display_name만 바꾸고 싶어도 username도 보내야 함
}
```

### PATCH 방식 — 올바른 설계

```python
# PATCH /users/{id} — 바꿀 것만 보내면 됨
{
  "display_name": "김강사"  # username은 보내지 않아도 됨
}
```

---
## 2. PATCH 구현 — Optional 필드와 exclude_unset
> PATCH를 위한 Pydantic 스키마는 모든 필드를 `Optional`로 만듭니다.

```python
from typing import Optional

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    # 보내지 않으면 None, 보내면 값이 들어옴
```

---
### [비추천] model_dump(): 보내지 않은 필드가 None으로 포함됨
```python
# 요청: {"display_name": "김강사"}
data = UserUpdate(display_name="김강사")

# model_dump() — 보내지 않은 필드가 None으로 포함됨
data.model_dump()
# {"display_name": "김강사"}  ← 이 경우엔 괜찮아 보이지만...
```
### [추천] model_dump(exclude_unset=True): 실제로 보낸 필드만
```python
# 예: username도 Optional이라면
# data.model_dump() → {"username": None, "display_name": "김강사"}
# → Supabase에 username=None으로 업데이트해서 데이터 손상!

# model_dump(exclude_unset=True) — 실제로 보낸 필드만
data.model_dump(exclude_unset=True)
# {"display_name": "김강사"}  ← username 제외
```

---
### Repository에서 PATCH 구현

```python
def update_user(self, user_id: str, data: UserUpdate) -> dict:
    payload = data.model_dump(exclude_unset=True)  # 보낸 필드만
    if not payload:
        raise HTTPException(status_code=400, detail="수정할 값이 없습니다")

    result = (
        self.db.table("app_users")
        .update(payload)
        .eq("id", user_id)
        .select("*")
        .execute()
    )
    return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")
```

---
### .select("*") 없으면 수정 전 데이터 반환
> .select("*") 없음 — result.data가 빈 리스트
```python
result = self.db.table("app_users").update(payload).eq("id", user_id).execute()
# result.data → []
```

> .select("*") 있음 — 수정된 행 반환
```python
result = self.db.table("app_users").update(payload).eq("id", user_id).select("*").execute()
# result.data → [{"id": "...", "display_name": "김강사", ...}]
```

---
## 3. Query 파라미터로 메시지 개수 제한

```python
from fastapi import Query

@app.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    #             ↑       ↑          ↑    ↑
    #           기본 50   최소 1   최대 100
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.list_messages(conversation_id, limit)
```

Swagger에서 `limit` 쿼리 파라미터가 자동으로 UI에 표시됩니다.

```
GET /conversations/{id}/messages?limit=20
```

---
## 4. 집계 API — Summary

사용자가 몇 개의 대화방과 메시지를 가지고 있는지 요약합니다.

```python
def summary(self, user_id: str) -> ChatSummary:
    conversations = self.list_conversations(user_id)
    message_count = 0
    for conv in conversations:
        ...

    return ChatSummary(
        user_id=user_id,
        conversation_count=len(conversations),
        message_count=message_count,
    )
```

---
## 5. 완성된 API 목록

```
POST   /users                              — 사용자 생성 (201)
GET    /users/{user_id}                    — 특정 사용자 조회
PATCH  /users/{user_id}                    — 사용자 정보 수정
GET    /users/{user_id}/summary            — 대화 수·메시지 수 요약
POST   /users/{user_id}/conversations      — 대화방 생성 (201)
GET    /users/{user_id}/conversations      — 사용자별 대화 목록
PATCH  /conversations/{conversation_id}    — 대화 제목 수정
POST   /conversations/{conversation_id}/messages  — 메시지 저장 (201)
GET    /conversations/{conversation_id}/messages  — 메시지 목록 (limit 파라미터)
```

---
## 핵심 패턴 요약

| 기능 | 코드 |
|------|------|
| PATCH 스키마 | `Optional[str] = Field(default=None, ...)` |
| 보낸 필드만 | `data.model_dump(exclude_unset=True)` |
| 수정 + 반환 | `.update(payload).eq("id", id).select("*").execute()` |
| Query 파라미터 | `limit: int = Query(default=50, ge=1, le=100)` |
| 집계 | `len(result.data)` |
| response_model | `@app.get(..., response_model=ChatSummary)` |
