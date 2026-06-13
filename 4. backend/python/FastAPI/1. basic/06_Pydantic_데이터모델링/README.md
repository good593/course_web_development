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
# Pydantic 기반 데이터 모델링

---
## 학습 목표

- Pydantic v2 BaseModel을 활용해 복잡한 데이터 구조를 선언할 수 있다
- Field()로 유효성 규칙과 문서화를 함께 관리할 수 있다
- field_validator / model_validator로 커스텀 검증 로직을 작성할 수 있다
- 입력/출력 스키마를 분리해 안전한 API를 설계할 수 있다


---

## [1. Pydantic란?](https://pydantic.dev/docs/validation/latest/get-started/)
- FastAPI는 내부적으로 **Pydantic**을 사용해 요청 데이터를 검증하고 직렬화합니다.  
- v2는 Rust 기반 코어(`pydantic-core`)로 재작성되어 v1 대비 약 5~50배 빠릅니다.

---
```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
```

선언만 하면:
- 타입 검증 (str → int 자동 변환 포함)
- JSON 직렬화 (`model.model_dump()`)
- JSON 역직렬화 (`User.model_validate(dict)`)
- Swagger 스키마 자동 생성

---
## 2. Field() — 필드 수준 제약

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="상품명 (2~100자)",
        examples=["맥북 프로"],
    )
    price: int = Field(
        gt=0,             # greater than 0
        le=10_000_000,    # less than or equal
        description="가격 (원)",
    )
    stock: int = Field(default=0, ge=0)
    sku: str = Field(pattern=r"^[A-Z]{2}-\d{4}$")  # 정규식
```

---
### 자주 쓰는 Field 옵션

| 옵션 | 의미 | 적용 타입 |
|------|------|----------|
| `default` | 기본값 | 모든 타입 |
| `default_factory` | 기본값 생성 함수 | 모든 타입 |
| `description` | Swagger 설명 | 모든 타입 |
| `examples` | Swagger 예시 | 모든 타입 |
| `alias` | JSON 키 별칭 | 모든 타입 |
| `gt` / `ge` | 초과 / 이상 | 숫자 |
| `lt` / `le` | 미만 / 이하 | 숫자 |
| `min_length` / `max_length` | 길이 범위 | 문자열, 리스트 |
| `pattern` | 정규식 | 문자열 |

---
## 3. 타입 시스템 활용

---
### Optional — 선택 필드

```python
from typing import Optional

class UpdateUser(BaseModel):
    name: Optional[str] = None       # None 허용
    bio: Optional[str] = None
    age: Optional[int] = None
```

`Optional[X]`는 `Union[X, None]`의 축약입니다.

---
### Union — 여러 타입 허용

```python
from typing import Union

class Notification(BaseModel):
    channel: Union[str, int]  # 채널명(str) 또는 채널ID(int)
    message: str
```

Python 3.10 이상에서는 `str | int` 문법도 사용 가능합니다.

---
### Literal — 허용 값 고정

```python
from typing import Literal

class Order(BaseModel):
    status: Literal["pending", "shipped", "delivered", "cancelled"]
    priority: Literal[1, 2, 3] = 2
```

`Literal`은 enum 대신 간단하게 허용 값을 고정할 때 사용합니다.

---
## 4. 중첩 모델 (Nested Models)

모델 안에 다른 모델을 필드로 사용할 수 있습니다.

```python
class Address(BaseModel):
    street: str
    city: str
    ...

class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    ...

class Order(BaseModel):
    order_id: str
    customer_name: str
    shipping_address: Address           # 단일 중첩
    items: List[OrderItem]              # 리스트 중첩
    coupon_code: Optional[str] = None
```

---
### 사용 예

```python
order_data = {
    "order_id": "ORD-001",
    "customer_name": "홍길동",
    "shipping_address": {
        "street": "강남대로 1길",
        "city": "서울",
        "zip_code": "06000"
    },
    "items": [
        {"product_id": 1, "quantity": 2, "unit_price": 15000},
        {"product_id": 3, "quantity": 1, "unit_price": 8500}
    ]
}

order = Order.model_validate(order_data)
print(order.shipping_address.city)   # 서울
print(order.items[0].quantity)       # 2
```

---
## 5. field_validator — 필드 단위 커스텀 검증

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("사용자명은 영문, 숫자, 밑줄(_)만 허용됩니다.")
        return v.lower()  # 반환값이 실제 저장될 값

    ...
```
> **v2 핵심 변경사항**: `@field_validator`는 반드시 `@classmethod`와 함께 사용하며, 첫 번째 파라미터는 `cls`입니다.

---
## 6. model_validator — 모델 전체 검증

여러 필드를 교차로 검증할 때 사용합니다.

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str
    max_days: int = 30

    @model_validator(mode="after")
    def check_date_range(self) -> "DateRange":
        from datetime import datetime
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        if end <= start:
            raise ValueError("종료일은 시작일보다 이후여야 합니다.")
        diff = (end - start).days
        ...
```

---
### mode 옵션

| mode | 실행 시점 | 사용 목적 |
|------|----------|----------|
| `"after"` | 모든 필드 파싱 완료 후 | 필드 간 교차 검증 (권장) |
| `"before"` | 파싱 전 (raw dict 상태) | 입력 데이터 전처리 |

---
## 7. model_config — 모델 설정

```python
from pydantic import BaseModel, ConfigDict

class StrictUser(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,   # 문자열 앞뒤 공백 자동 제거
        str_to_lower=True,           # 문자열 소문자 변환
        validate_assignment=True,    # 속성 재할당 시에도 검증
        frozen=True,                 # 불변 모델 (hash 가능)
        populate_by_name=True,       # alias와 원래 이름 모두 허용
    )

    name: str
    email: str
```

---
## 8. 입력/출력 스키마 분리 패턴

API 설계에서 **입력(Input)**과 **출력(Output)**에 다른 필드 집합을 사용하는 패턴입니다.

```python
# ── 생성 요청 (클라이언트 → 서버) ──────────────────
class UserCreate(UserBase):
    password: str = Field(min_length=8)  # 입력에만 존재

# ── 응답 (서버 → 클라이언트) ────────────────────────
class UserResponse(UserBase):
    id: int
    created_at: datetime
    # password 필드 없음 → 절대 노출되지 않음

    model_config = ConfigDict(from_attributes=True)
```

> `from_attributes=True`는 SQLAlchemy ORM 객체처럼 dict가 아닌 객체에서 모델을 생성할 때 필요합니다.

---
## 핵심 정리

| 도구 | 용도 |
|------|------|
| `Field()` | 필드별 제약 조건 + Swagger 문서화 |
| `Optional[T]` | 선택 필드 (None 허용) |
| `Literal[...]` | 허용 값 고정 (enum 대용) |
| 중첩 모델 | 복잡한 구조 표현 |
| `field_validator` | 단일 필드 커스텀 검증 |
| `model_validator` | 다중 필드 교차 검증 |
| `model_config` | 모델 전역 동작 설정 |
| 스키마 분리 | 입력/출력 필드 격리로 보안 강화 |
