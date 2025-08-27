 # app/models/video.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from app.db.base import Base

class Video(Base):
    __tablename__ = "videos"
    video_id = Column(Integer, primary_key=True, index=True,  autoincrement=True) # PK
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False) #FK
    video_title = Column(String, nullable=False)
    upload_date = Column(Date, default=date.today)

    user = relationship("User", back_populates="videos", passive_deletes=True)
    keywords = relationship("Keyword", back_populates="video", cascade="all, delete-orphan")  # 비디오 모델에 키워드 관계 추가
    feedback = relationship("VideoFeedback", back_populates="video", uselist=False, cascade="all, delete-orphan")

    # 입력된 객체 확인을(디버깅이나 로깅) 위해 사용
    def __repr__(self):
        return f"<Video(video_id={self.video_id}, title='{self.video_title}', date={self.upload_date})>"
