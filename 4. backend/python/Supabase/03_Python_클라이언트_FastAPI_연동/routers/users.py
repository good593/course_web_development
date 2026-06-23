from fastapi import APIRouter, HTTPException

from database import supabase
from schemas import UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


def first_or_404(rows: list[dict], detail: str) -> dict:
    """조회 결과의 첫 행을 반환하고, 결과가 없으면 404 오류를 발생시킵니다."""
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


# @router.post는 함수와 HTTP POST 요청을 연결합니다.
# status_code=201은 리소스 생성 성공을 나타내는 HTTP 상태 코드입니다.
@router.post("", status_code=201)
def create_user(data: UserCreate):
    # model_dump()는 검증된 Pydantic 모델을 Supabase에 전달할 딕셔너리로 바꿉니다.
    result = (
        # table()은 대상 테이블, insert()는 새 행에 저장할 값을 지정합니다.
        supabase.table("app_users")
        # insert()는 기본적으로 생성된 행을 result.data로 반환합니다.
        .insert(data.model_dump())
        # 메서드로 만든 쿼리는 execute()를 호출해야 실제로 실행됩니다.
        .execute()
    )
    return first_or_404(result.data, "사용자가 생성되지 않았습니다")


@router.get("")
def list_users():
    result = (
        supabase.table("app_users")
        .select("*")
        # 최신 사용자가 먼저 오도록 생성 시각을 내림차순으로 정렬합니다.
        .order("created_at", desc=True)
        .execute()
    )
    # 실행 결과의 실제 행 목록은 result.data에 들어 있습니다. 결과가 없으면 []입니다.
    return result.data
