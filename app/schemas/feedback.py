# app/schemas/feedback.py
from typing import List
from pydantic import BaseModel
from app.schemas.youtube import YoutubeTitleResponse

class FeedbackResponse(BaseModel):
    titles: List[str]
    hashtags: List[str]
    similar_videos: List[YoutubeTitleResponse]
