# app/models/youtube.py
from sqlalchemy import Column, String, Text, DateTime, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base
from pgvector.sqlalchemy import Vector  # 벡터 컬럼 추가

class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    video_id = Column(String(255), primary_key=True, index=True)  # 유튜브 videoId
    title = Column(String(255), nullable=False)             # 영상 제목
    description = Column(Text, nullable=True)               # 영상 설명
    published_at = Column(DateTime, nullable=False)         # 업로드 시간
    channel_title = Column(String(255), nullable=True)      # 채널 이름
    tags = Column(JSON, nullable=True)                      # 태그 리스트(JSON)
    thumbnail_url = Column(Text, nullable=True)             # 썸네일 URL
    video_url = Column(Text, nullable=True)                 # 유튜브 영상 URL
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)  # DB 저장 시각
    embedding = Column(Vector(384), nullable=True)          # 임베딩 벡터 컬럼

    def __repr__(self):
        return f"<YouTubeVideo(id={self.video_id}, title={self.title}, channel={self.channel_title})>"
