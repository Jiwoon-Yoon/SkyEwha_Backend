from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.keyword import WhisperProcessRequest
from app.services.video_pipeline import process_video_for_keywords
from app.crud.crud_video import get_video_by_id

router = APIRouter()

@router.post("/process_keywords/")
def process_keywords(
    request: WhisperProcessRequest,
    db: Session = Depends(deps.get_db),
):
    video = get_video_by_id(db, video_id= request.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # video.user_id, video.video_title 정보로 키워드 처리 호출
    process_video_for_keywords(
        db=db,
        user_id=video.user_id,
        video_title=video.video_title,
        video_id=video.video_id,
    )

    return {"message": "키워드 처리 완료"}
