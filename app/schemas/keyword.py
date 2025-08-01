# app/schemas/keyword.py
from pydantic import BaseModel

class WhisperProcessRequest(BaseModel):
    video_id: int

class KeywordCreate(BaseModel):
    video_id: int
    keyword: str
    embedding: list[float] | None = None