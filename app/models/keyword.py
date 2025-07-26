from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from pgvector.sqlalchemy import Vector

class Keyword(Base):
    __tablename__ = "keywords"

    keyword_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False) #FK
    keyword = Column(String, nullable=False)
    embedding = Column(Vector(384), nullable=True)  # 예: 384차원 벡터, 모델에 따라 조정 가능

    video = relationship("Video", back_populates="keywords", passive_deletes=True)

    def __repr__(self):
        return f"<Keyword(id={self.keyword_id}, video_id={self.video_id}, keyword='{self.keyword}')>"
