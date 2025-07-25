# app/crud/crud_youtube.py

from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.youtube import YouTubeVideo
from app.schemas.youtube import YoutubeVideoCreate


def save_videos_to_db(videos: List[YoutubeVideoCreate], db: Session) -> None:
    """
    유튜브 영상 리스트를 DB에 저장합니다.
    중복 영상(예: video_id가 같은 영상)은 저장하지 않습니다.
    """
    for video in videos:
        # 중복 체크
        existing = db.query(YouTubeVideo).filter(
            YouTubeVideo.video_id == video.video_id
        ).first()
        if existing:
            continue

        db_video = YouTubeVideo(
            video_id=video.video_id,
            title=video.title,
            description=video.description,
            published_at=video.published_at,
            channel_title=video.channel_title,
            tags=video.tags if video.tags else None,
            thumbnail_url=str(video.thumbnail_url) if video.thumbnail_url else None,
            video_url=str(video.video_url) if video.video_url else None,
        )

        db.add(db_video)

    db.commit()
