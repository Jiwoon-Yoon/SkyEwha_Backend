# app/api/v1/youtube/bookmark_routes.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.auth import get_current_user  # 이미 있을 거라고 가정
from app.models.user import User
from app.crud import crud_video_bookmark, crud_youtube
from app.schemas.video_bookmark import VideoBookmarkItem

router = APIRouter()

@router.post(
    "/videos/{video_id}/bookmark",
    status_code=status.HTTP_201_CREATED,
    summary="영상 북마크 추가",
)
def add_bookmark(
    response: Response,
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1) 영상 존재 여부 확인
    video = crud_youtube.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 2) 이미 북마크인지 확인
    existing = crud_video_bookmark.get_bookmark(
        db, user_id=current_user.user_id, video_id=video_id
    )
    if existing:
        response.status_code = status.HTTP_200_OK
        return {"message": "이미 북마크 되어 있습니다."}

    crud_video_bookmark.create_bookmark(db, current_user.user_id, video_id)
    return {"message": "북마크가 추가되었습니다."}


@router.delete(
    "/videos/{video_id}/bookmark",
    status_code=status.HTTP_200_OK,
    summary="영상 북마크 해제",
)
def remove_bookmark(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = crud_video_bookmark.delete_bookmark(
        db, user_id=current_user.user_id, video_id=video_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="북마크가 존재하지 않습니다.")
    return {"message": "북마크가 해제되었습니다."}


@router.get(
    "/videos/bookmarks/me",
    response_model=List[VideoBookmarkItem],
    summary="내가 북마크한 영상 목록",
)
def list_my_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = crud_video_bookmark.get_bookmarks_with_videos(
        db, user_id=current_user.user_id
    )

    result: List[VideoBookmarkItem] = []
    for bookmark, video in rows:
        item = VideoBookmarkItem(
            video_id=video.video_id,
            title=video.title,
            video_url=video.video_url,
            thumbnail_url=video.thumbnail_url,
            channel_title=video.channel_title,
            published_at=video.published_at,
            view_count=video.view_count,
            bookmarked_at=bookmark.created_at,
        )
        result.append(item)

    return result
