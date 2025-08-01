# app/crud/crud_keyword.py
from sqlalchemy.orm import Session
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate

def create_keyword(db: Session, keyword_data: KeywordCreate) -> Keyword:
    db_keyword = Keyword(**keyword_data.model_dump())
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword
