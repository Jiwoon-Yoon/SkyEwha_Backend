# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, UniqueConstraint, BigInteger
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # PK
    user_name = Column(String(50), nullable=True)
    user_email = Column(String(255), unique=True, index=True, nullable=True)  # 이메일 (고유값, NULL 허용)
    user_nickname = Column(String(50), index=True, nullable=False)  # 닉네임 (중복 가능, NOT NULL)
    user_provider = Column(String(20), nullable=False)  # 예: 'kakao', 'google'
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 가입일
    user_is_active = Column(Boolean, default=True)  # 계정 활성화 상태 (기본값: True)
    user_last_login = Column(DateTime, default=None)  # 마지막 로그인 시간 (NULL 허용)
    user_social_id = Column(String(255), unique=True, nullable=True)  # 카카오/구글/네이버 계정 고유 ID (고유값, NULL 허용)

    __table_args__ = (
        UniqueConstraint("user_social_id","user_provider",name="uix_social_provider"),
    )

    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")  # video가 user를 참조
    content_feedbacks = relationship("ContentFeedback", back_populates="user", cascade="all, delete-orphan") #content_feedback이 user를 참조
    video_bookmarks = relationship("VideoBookmark", back_populates="user", cascade="all, delete-orphan")
    
    # 입력된 객체 확인을(디버깅이나 로깅) 위해 사용
    def __repr__(self):
        return f"<User(user_id={self.user_id}, user_email={self.user_email}, user_nickname={self.user_nickname})>"