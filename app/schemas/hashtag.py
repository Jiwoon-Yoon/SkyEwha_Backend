# app/schemas/hashtag.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class HashtagBase(BaseModel):
    hashtag: str
    week_posts: int

class HashtagCreate(HashtagBase):
    pass

class HashtagInDB(HashtagBase):
    id: int
    total_posts: Optional[int]
    view_weight: Optional[float]
    embedding: Optional[list[float]] = None  # 선택사항
    last_updated: date

    model_config = {
        "from_attributes": True
    }
