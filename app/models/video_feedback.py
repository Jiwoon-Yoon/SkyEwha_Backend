# app/models/video_feedback.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class VideoFeedback(Base):
    __tablename__ = "video_feedback"
    video_id = Column(Integer, ForeignKey("videos.video_id", ondelete="CASCADE"), primary_key=True)
    titles = Column(JSON, nullable=True)
    hashtags = Column(JSON, nullable=True)
    similar_videos = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    video = relationship("Video", back_populates="feedback", passive_deletes=True)

    def __repr__(self):
        return f"<VideoFeedback(video_id={self.video_id}, updated_at={self.updated_at})>"
