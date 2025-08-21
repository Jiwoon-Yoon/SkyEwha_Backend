#app/api/v1/feedback/hashtag_feedback.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from typing import List
from app.services.hashtag_service import recommend_hashtags_from_keywords
from app.crud.crud_video import get_video_by_id

router = APIRouter()

@router.get("/{video_id}", response_model=List[str])
def recommend_hashtags(video_id: int, db: Session = Depends(deps.get_db)):
    video = get_video_by_id(db, video_id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return recommend_hashtags_from_keywords(db, video_id=video_id, top_n=10)
