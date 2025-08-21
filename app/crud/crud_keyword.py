# app/crud/crud_keyword.py
from sqlalchemy.orm import Session
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate
from typing import List

def create_keyword(db: Session, keyword_data: KeywordCreate) -> Keyword:
    db_keyword = Keyword(**keyword_data.model_dump())
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

def get_keywords_by_video_id(db: Session, video_id: int) -> List[str]:
    keywords = db.query(Keyword).filter(Keyword.video_id == video_id).all()
    return [k.keyword for k in keywords]

def get_keywords_with_embeddings_by_video_id(db: Session, video_id: int) -> List[Keyword]:
    """키워드 + 임베딩까지 반환"""
    return db.query(Keyword).filter(
        Keyword.video_id == video_id,
        Keyword.embedding != None
    ).all()