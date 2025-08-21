# app/api/v1/feedback/feedback_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.crud_video import get_video_by_id
from app.services.feedback_service import (
    recommend_titles,
    recommend_hashtags,
    recommend_similar_videos,
)
from app.schemas.feedback import FeedbackResponse

router = APIRouter()

@router.get("/{video_id}", response_model=FeedbackResponse)
def get_feedback(video_id: int, db: Session = Depends(get_db)):
    video = get_video_by_id(db, video_id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        titles = recommend_titles(db, video_id)
        hashtags = recommend_hashtags(db, video_id)
        similar_videos = recommend_similar_videos(db, video_id)

        return FeedbackResponse(
            titles=titles,
            hashtags=hashtags,
            similar_videos=similar_videos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 생성 실패: {e}")
