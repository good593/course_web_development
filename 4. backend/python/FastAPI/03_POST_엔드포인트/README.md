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
# POST 엔드포인트 구현
- 데이터를 **Request Body에 포함**
- **생성 / 처리** 목적
- URL에 데이터가 노출되지 않음
- 데이터 크기 제한 없음
- 민감한 정보 전송 가능

---
## GET vs POST

| 항목 | GET | POST |
|------|-----|------|
| 데이터 위치 | URL Query String | Request Body |
| 데이터 크기 | 제한 있음 | 제한 없음 |
| 보안 | URL에 노출 | Body에 숨김 |
| 캐싱 | 가능 | 불가 |
| 목적 | 조회 | 생성/처리 |

---
## 1. Request Body와 Pydantic BaseModel

> POST는 데이터를 URL이 아닌 Body에 담습니다.
> FastAPI에서는 Pydantic BaseModel이 이 Body를 자동으로 받아 검증합니다.

```shell
POST /items HTTP/1.1
Content-Type: application/json

{
    "name": "키보드",
    "price": 89000,
    "category": "전자기기"
}
```

---
### BaseModel로 Body 스키마 정의

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True   # 기본값 있는 선택 필드
```

---
```python
@app.post("/items")
def create_item(item: ItemCreate):
    #            ↑↑↑↑
    #   Body 데이터 자동 파싱 + 검증
    return item
```

FastAPI가 자동으로 처리하는 것:
- JSON → Python 객체 변환
- 타입 검증 (price에 문자열이 오면 422 반환)
- 필수 필드 누락 시 422 반환
- Swagger UI에 Body 스키마 자동 문서화

---
## 2. Field로 유효성 규칙 추가

---
### 기본 Field 사용법

```python
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="아이템 이름",
        examples=["노트북"],
    )
    price: float = Field(
        gt=0,                     # greater than 0 (0 초과)
        description="가격 (0보다 커야 함)",
        examples=[15000],
    )
    in_stock: bool = Field(
        default=True,
        description="재고 여부",
    )
```

---
### 주요 Field 검증 옵션

| 옵션 | 적용 타입 | 의미 |
|------|----------|------|
| `min_length` | str | 최소 길이 |
| `max_length` | str | 최대 길이 |
| `pattern` | str | 정규표현식 패턴 |
| `gt` | int/float | 초과 (greater than) |
| `ge` | int/float | 이상 (greater or equal) |
| `lt` | int/float | 미만 (less than) |
| `le` | int/float | 이하 (less or equal) |
| `default` | 모든 타입 | 기본값 |

---
### 이메일 검증
```python
from pydantic import BaseModel, EmailStr

# pip install pydantic[email] 필요
class UserCreate(BaseModel):
    name: str
    email: EmailStr   # 이메일 형식 자동 검증
    password: str = Field(min_length=8)
```

---
## 3. 입력/출력 스키마 분리

입력(요청)과 출력(응답)에 필요한 필드가 다른 경우 스키마를 분리한다.

```python
# 입력 스키마 (클라이언트 → 서버)
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    category: str
    in_stock: bool = True

# 출력 스키마 (서버 → 클라이언트)
class ItemResponse(BaseModel):
    id: int              # 서버가 생성
    name: str
    price: float
    category: str
    in_stock: bool
    created_at: datetime  # 서버가 생성
```

---
## 4. 422 에러 응답 분석

```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "name"],
            "msg": "Field required",
            "input": {"price": 100}
        },
        ...
    ]
}
```
- `loc` : 오류 위치 (`body` → `필드명`)
- `type` : 오류 종류
- `msg` : 오류 메시지

---
## 5. 서버 실행 및 Swagger 실습

---
### 가상환경 생성
```bash
# pyproject.toml과 uv.lock 기준으로 의존성 설치
uv sync
```

### 서버 실행

```bash
python -m uvicorn main:app --reload --port 8001
```

---
### Swagger UI 실습 (http://localhost:8001/docs)

> 각 API에서 **Try it out**을 누른 뒤 아래 순서대로 입력합니다.




