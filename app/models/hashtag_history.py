# app/models/hashtag_history.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String, Date

class HashtagHistory(Base):
    __tablename__ = "hashtag_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hashtag = Column(String, nullable=False)
    week_posts = Column(Integer, nullable=False)
    collected_at = Column(Date, nullable=False)  # 해당 주 데이터
