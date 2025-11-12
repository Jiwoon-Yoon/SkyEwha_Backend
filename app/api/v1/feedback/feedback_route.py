# app/api/v1/feedback/feedback_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.crud.crud_video import get_video_by_id
from app.crud.crud_content_feedback import get_feedbacks_by_user_id, get_content_feedback_by_feedback_id
from app.services.feedback_service import (
    recommend_titles,
    recommend_hashtags,
    recommend_similar_videos,
)
from app.schemas.feedback import FeedbackResponse
from app.crud.crud_content_feedback import upsert_content_feedback_by_feedback_id

router = APIRouter()

@router.get("/my-feedbacks", response_model=List[FeedbackResponse])
def read_my_feedbacks(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    로그인한 사용자의 모든 비디오 피드백 조회
    """
    try:
        feedbacks = get_feedbacks_by_user_id(db, user_id=current_user.user_id)
        # 필수 컬럼이 None인 데이터는 필터링
        filtered_feedbacks = [
            feedback for feedback in feedbacks
            # 다음 4가지 필드가 모두 None이 아니고, 빈 문자열이 아니고, 빈 리스트가 아닌 경우만 통과
            if (feedback.source_title and
                feedback.titles and
                feedback.hashtags and
                feedback.similar_videos)
        ]
        # 필터링 후 데이터가 없는 경우 404 반환
        if not filtered_feedbacks:
            # 원본 DB 데이터는 있었으나, 필수 컬럼 결측으로 모두 제외된 경우 포함
            raise HTTPException(status_code=404, detail="조건을 만족하는 피드백이 존재하지 않습니다.")

        return filtered_feedbacks
        # if not feedbacks:
        #     raise HTTPException(status_code=404, detail="해당 사용자의 피드백이 존재하지 않습니다.")
        # return feedbacks
    except HTTPException:
        # HTTPException (404)은 다시 발생시킵니다.
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 조회 중 오류 발생: {e}")


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    content = get_content_feedback_by_feedback_id(db, feedback_id=feedback_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    try:
        titles = recommend_titles(db, feedback_id)
        hashtags = recommend_hashtags(db, feedback_id)
        similar_videos = recommend_similar_videos(db, feedback_id)

        #feedbackResponse 객체 생성
        feedback_response = FeedbackResponse(
            titles=titles,
            hashtags=hashtags,
            similar_videos=similar_videos,
        )


        # DB에 저장 / 업데이트
        upsert_content_feedback_by_feedback_id(db, feedback_id=feedback_id, feedback=feedback_response)
        return feedback_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 생성 실패: {e}")
