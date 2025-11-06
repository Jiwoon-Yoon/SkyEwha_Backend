# app/crud/crud_video_bookmark.py
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.video_bookmark import VideoBookmark
from app.models.youtube import YouTubeVideo


def get_bookmark(
    db: Session,
    user_id: int,
    video_id: str,
) -> Optional[VideoBookmark]:
    return (
        db.query(VideoBookmark)
        .filter(
            VideoBookmark.user_id == user_id,
            VideoBookmark.video_id == video_id,
        )
        .first()
    )


def create_bookmark(
    db: Session,
    user_id: int,
    video_id: str,
) -> VideoBookmark:
    bookmark = VideoBookmark(
        user_id=user_id,
        video_id=video_id,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def delete_bookmark(
    db: Session,
    user_id: int,
    video_id: str,
) -> bool:
    bookmark = get_bookmark(db, user_id, video_id)
    if not bookmark:
        return False

    db.delete(bookmark)
    db.commit()
    return True


def get_bookmarks_with_videos(
    db: Session,
    user_id: int,
) -> List[Tuple[VideoBookmark, YouTubeVideo]]:
    """
    북마크 + 영상 정보 같이 가져오기
    (A안: 라우터에서 직접 Pydantic으로 매핑)
    """
    rows = (
        db.query(VideoBookmark, YouTubeVideo)
        .join(
            YouTubeVideo,
            VideoBookmark.video_id == YouTubeVideo.video_id,
        )
        .filter(VideoBookmark.user_id == user_id)
        .order_by(VideoBookmark.created_at.desc())
        .all()
    )
    return rows
