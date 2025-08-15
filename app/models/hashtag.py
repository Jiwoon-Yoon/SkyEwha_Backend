# app/models/hashtag.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String, BigInteger, Float, Date
from pgvector.sqlalchemy import Vector

class Hashtag(Base):
    __tablename__ = "hashtags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) #PK
    hashtag = Column(String, nullable=False, unique=True)
    embedding = Column(Vector(384))  # 384차원 예시, 모델에 맞게 수정
    week_posts = Column(Integer, nullable=True)
    total_posts = Column(BigInteger, nullable=True)
    view_weight = Column(Float, nullable=True) # 조회수 기반 가중치
    last_updated = Column(Date, nullable=False)