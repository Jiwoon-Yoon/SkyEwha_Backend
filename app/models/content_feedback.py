 # app/models/content_feedback.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime
from sqlalchemy.orm import relationship
from datetime import date
from app.db.base import Base

class ContentFeedback(Base):
     __tablename__ = "content_feedback"

     # 새로운 독립적인 기본 키 (Primary Key)
     feedback_id = Column(Integer, primary_key=True, index=True)

     # 입력 소스 타입 구분 (예: 'video', 'text')
     source_type = Column(String, nullable=False)
     source_title = Column(String, nullable=False)

     # 기존 video_id는 외래 키 (텍스트 입력의 경우 NULL 허용)
     video_id = Column(Integer, ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=True)
     # 사용자 ID (외래 키) - 누가 이 분석 결과를 생성했는지 기록
     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

     input_text = Column(String, nullable=True)

     titles = Column(JSON, nullable=True)
     hashtags = Column(JSON, nullable=True)
     similar_videos = Column(JSON, nullable=True)
     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

     # video와의 관계는 유지 (있을 경우만)
     video = relationship("Video", back_populates="feedbacks", passive_deletes=True) #content_feedback이 video를 참조
     user = relationship("User", back_populates="content_feedbacks", passive_deletes=True) #content_feedback이 user를 참조

     keywords = relationship("Keyword", back_populates="feedback", cascade="all, delete-orphan") #keyword가 content_feedback을 참조

     def __repr__(self):
         return f"<ContentFeedback(feedback_id={self.feedback_id}, source_type={self.updated_at})>"
