from fastapi import APIRouter, Depends, Query

import schemas
from core.dependencies import get_post_service
from services import PostService

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get("", response_model=list[schemas.PostResponse])
def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    published_only: bool = False,
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(
        skip=skip,
        limit=limit,
        category_id=category_id,
        published_only=published_only,
    )


@router.get("/{post_id}", response_model=schemas.PostDetailResponse)
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.get_post_detail(post_id)


@router.post("", response_model=schemas.PostResponse, status_code=201)
def create_post(
    data: schemas.PostCreate,
    service: PostService = Depends(get_post_service),
):
    return service.create_post(data)


@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    data: schemas.PostUpdate,
    service: PostService = Depends(get_post_service),
):
    return service.update_post(post_id, data)


@router.post("/{post_id}/publish", response_model=schemas.PostResponse)
def publish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.publish_post(post_id)


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    service.delete_post(post_id)
