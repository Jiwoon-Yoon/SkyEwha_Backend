#app/api/v1/feedback/hashtag_feedback.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from typing import List
from app.services.hashtag_service import recommend_hashtags_from_keywords
from app.crud.crud_video import get_video_by_id
from app.crud.crud_content_feedback import get_content_feedback_by_feedback_id, get_content_feedback_by_video_id

router = APIRouter()

# @router.get("/video/{video_id}", response_model=List[str])
# def recommend_hashtags_by_video_id(video_id: int, db: Session = Depends(deps.get_db)):
#     """
#     영상 ID(video_id)를 기반으로 해시태그를 추천합니다.
#     """
#     # 1. video_id로 ContentFeedback 레코드를 찾습니다.
#     # VideoFeedback 대신 ContentFeedback 사용
#     feedback = get_content_feedback_by_video_id(db, video_id=video_id)
#     if not feedback:
#         # 영상이 있지만 아직 피드백 분석이 완료되지 않은 경우
#         raise HTTPException(status_code=404, detail="Analysis results not found for this video")
#
#     # 2. ContentFeedback ID를 사용하여 추천 서비스 호출
#     # recommend_hashtags_from_keywords 함수는 이제 feedback_id를 사용해야 합니다.
#     return recommend_hashtags_from_keywords(
#         db,
#         feedback_id=feedback.feedback_id,
#         top_n=10
#     )


@router.get("/feedback/{feedback_id}", response_model=List[str])
def recommend_hashtags_by_feedback_id(feedback_id: int, db: Session = Depends(deps.get_db)):
    """
    ContentFeedback ID(feedback_id)를 기반으로 해시태그를 추천합니다.
    (텍스트 입력 결과를 포함하는 통합 엔드포인트)
    """
    # 1. feedback_id로 ContentFeedback 레코드를 조회
    feedback = get_content_feedback_by_feedback_id(db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback record not found")

    # 2. ContentFeedback ID를 사용하여 추천 서비스 호출
    return recommend_hashtags_from_keywords(
        db,
        feedback_id=feedback.feedback_id,
        top_n=10
    )
