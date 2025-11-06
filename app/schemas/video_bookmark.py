# app/schemas/video_bookmark.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class VideoBookmarkItem(BaseModel):
    """
    '내 북마크 목록' 같은 곳에서 쓸 응답 스키마
    북마크 정보 + 영상 요약 정보
    """
    video_id: str                      # YouTubeVideo.video_id
    title: str
    video_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    channel_title: Optional[str] = None
    published_at: datetime
    view_count: Optional[int] = 0
    # 북마크한 시각
    bookmarked_at: datetime
