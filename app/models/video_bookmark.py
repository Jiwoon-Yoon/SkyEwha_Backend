# app/models/video_bookmark.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class VideoBookmark(Base):
    __tablename__ = "video_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uix_user_video_bookmark"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    video_id = Column(String(255), ForeignKey("youtube_videos.video_id", ondelete="CASCADE"), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # 관계 설정
    user = relationship("User", back_populates="video_bookmarks")
    video = relationship("YouTubeVideo", back_populates="bookmarks")

    def __repr__(self):
        return f"<VideoBookmark(user_id={self.user_id}, video_id={self.video_id})>"