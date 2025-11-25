# app/schemas/feedback.py
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.youtube import YoutubeTitleResponse

class FeedbackResponse(BaseModel):
    source_title: Optional[str] = None
    titles: Optional[List[str]] = []
    hashtags: Optional[List[str]] = []
    similar_videos: Optional[List[YoutubeTitleResponse]] = []
