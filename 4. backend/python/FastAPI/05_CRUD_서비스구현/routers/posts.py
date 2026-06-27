from fastapi import APIRouter, HTTPException, Query

import schemas
from models.blog import blog_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.get(
    "",
    response_model=schemas.PaginatedPosts,
    summary="게시글 목록",
)
def list_posts(
    skip: int = Query(0, ge=0, description="건너뛸 게시글 수"),
    limit: int = Query(10, ge=1, le=50, description="가져올 게시글 수"),
    published_only: bool = Query(False, description="공개 게시글만 조회"),
    search: str | None = Query(None, description="제목 또는 본문 키워드"),
):
    return blog_db.list_posts(
        skip=skip,
        limit=limit,
        published_only=published_only,
        search=search,
    )


@router.post(
    "",
    response_model=schemas.PostResponse,
    status_code=201,
    summary="게시글 생성",
)
def create_post(post: schemas.PostCreate):
    return blog_db.create_post(post)


@router.get(
    "/{post_id}",
    response_model=schemas.PostResponse,
    summary="게시글 상세",
)
def get_post(post_id: int):
    post = blog_db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return post


@router.patch(
    "/{post_id}",
    response_model=schemas.PostResponse,
    summary="게시글 수정",
)
def update_post(post_id: int, post: schemas.PostUpdate):
    if not blog_db.get_post(post_id):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    return blog_db.update_post(post_id, post)


@router.post(
    "/{post_id}/publish",
    response_model=schemas.PostResponse,
    summary="게시글 공개",
)
def publish_post(post_id: int):
    if not blog_db.get_post(post_id):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return blog_db.update_post(post_id, schemas.PostUpdate(published=True))


@router.delete(
    "/{post_id}",
    status_code=204,
    summary="게시글 삭제",
)
def delete_post(post_id: int):
    if not blog_db.delete_post(post_id):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
