from fastapi import APIRouter, Depends, Query

import schemas
from core.dependencies import get_post_service
from services import PostService

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get(
    "",
    response_model=schemas.PaginatedPosts,
    summary="게시글 목록 (페이징, 검색, 필터)",
)
def list_posts(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 항목 수"),
    category_id: int | None = Query(None, description="카테고리 필터"),
    published_only: bool = Query(False, description="공개 게시글만"),
    search: str | None = Query(None, description="제목 키워드 검색"),
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(
        skip=skip,
        limit=limit,
        category_id=category_id,
        published_only=published_only,
        search=search,
    )


@router.get(
    "/{post_id}",
    response_model=schemas.PostDetailResponse,
    summary="게시글 상세 (카테고리 + 댓글 포함)",
)
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.get_post_detail(post_id)


@router.post(
    "",
    response_model=schemas.PostResponse,
    status_code=201,
    summary="게시글 생성",
)
def create_post(data: schemas.PostCreate, service: PostService = Depends(get_post_service)):
    return service.create_post(data)


@router.patch(
    "/{post_id}",
    response_model=schemas.PostResponse,
    summary="게시글 수정",
)
def update_post(post_id: int, data: schemas.PostUpdate, service: PostService = Depends(get_post_service)):
    return service.update_post(post_id, data)


@router.post(
    "/{post_id}/publish",
    response_model=schemas.PostResponse,
    summary="게시글 공개",
)
def publish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.publish_post(post_id)


@router.post(
    "/{post_id}/unpublish",
    response_model=schemas.PostResponse,
    summary="게시글 비공개",
)
def unpublish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.unpublish_post(post_id)


@router.delete(
    "/{post_id}",
    status_code=204,
    summary="게시글 삭제 (댓글 포함)",
)
def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    service.delete_post(post_id)
