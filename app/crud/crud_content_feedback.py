#app/crud/crud_content_feedback.py
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, Union, List
from datetime import datetime

from app.models.content_feedback import ContentFeedback
from app.schemas.content_feedback import ContentFeedbackCreate, ContentFeedbackUpdate
from app.schemas.feedback import FeedbackResponse
from app.schemas.youtube import YoutubeTitleResponse

def get_content_feedback_by_feedback_id(db: Session, feedback_id: int) -> Optional[ContentFeedback]:
    """주어진 feedback_id로 ContentFeedback 레코드를 조회합니다."""
    return db.query(ContentFeedback).filter(ContentFeedback.feedback_id == feedback_id).first()


def get_content_feedback_by_video_id(db: Session, video_id: int) -> Optional[ContentFeedback]:
    """
    video_id로 ContentFeedback 레코드를 조회합니다.
    """
    return db.query(ContentFeedback).filter(ContentFeedback.video_id == video_id).first()


def create_content_feedback(db: Session, user_id: int, feedback_in: ContentFeedbackCreate) -> ContentFeedback:
    """
    새로운 ContentFeedback 레코드를 생성합니다. (텍스트/영상 파이프라인 시작 단계에 사용)
    """
    feedback_data = feedback_in.model_dump(exclude_unset=True)
    #db_feedback = ContentFeedback(**feedback_data)
    db_feedback = ContentFeedback(**feedback_data, user_id=user_id)

    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def update_content_feedback(
        db: Session,
        feedback_id: int,
        feedback_update: Union[ContentFeedbackUpdate, Dict[str, Any]]
) -> Optional[ContentFeedback]:
    """
    ContentFeedback 레코드를 업데이트합니다. (AI 분석 결과 저장 단계에 사용)
    """
    db_feedback = get_content_feedback_by_feedback_id(db, feedback_id)

    if not db_feedback:
        return None

    if isinstance(feedback_update, dict):
        update_data = feedback_update
    else:
        update_data = feedback_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            setattr(db_feedback, field, value)

    db_feedback.updated_at = datetime.now()

    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    return db_feedback


def upsert_content_feedback_by_feedback_id(db: Session, feedback_id: int,
                                        feedback: FeedbackResponse) -> ContentFeedback:
    """
    VideoFeedback을 ContentFeedback으로 대체하여 upsert합니다. update + insert
    - video_id로 기존 레코드를 찾거나 새로 생성합니다.
    - video_pipeline의 최종 업데이트 단계에 사용됩니다.
    """
    db_feedback = get_content_feedback_by_feedback_id(db, feedback_id)

    # JSON 컬럼 저장용 직렬화 (published_at 처리 포함)
    similar_videos_serializable = [
        {
            **sv.model_dump(),
            "published_at": sv.published_at.isoformat() if sv.published_at else None
        }
        for sv in feedback.similar_videos
    ]

    if db_feedback:
        # 기존 레코드 업데이트 (update_fields 딕셔너리 없이 직접 할당)
        db_feedback.titles = feedback.titles
        db_feedback.hashtags = feedback.hashtags
        db_feedback.similar_videos = similar_videos_serializable
        db_feedback.updated_at = datetime.now()
    # else:
    #     # 새 레코드 생성
    #     db_feedback = ContentFeedback(
    #         feedback_id=feedback_id,
    #         source_type="video",
    #         source_title=feedback.titles,
    #         titles=feedback.titles,
    #         hashtags=feedback.hashtags,
    #         similar_videos=similar_videos_serializable,
    #         updated_at=datetime.now()
    #     )
    #     db.add(db_feedback)

    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def delete_content_feedback(db: Session, feedback_id: int) -> bool:
    """
    feedback_id 기반으로 피드백 삭제 (텍스트 또는 영상 모두 가능)
    """
    db_feedback = get_content_feedback_by_feedback_id(db, feedback_id)
    if not db_feedback:
        return False
    db.delete(db_feedback)
    db.commit()
    return True


def delete_content_feedback_by_video_id(db: Session, video_id: int) -> bool:
    """
    video_id 기반으로 피드백 삭제
    """
    db_feedback = get_content_feedback_by_video_id(db, video_id)
    if not db_feedback:
        return False
    db.delete(db_feedback)
    db.commit()
    return True


def get_feedbacks_by_user_id(db: Session, user_id: int) -> List[FeedbackResponse]:
    """
    특정 user_id의 모든 ContentFeedback 조회 후 FeedbackResponse 리스트로 반환
    (기존 get_feedbacks_by_user_id 함수 대체)
    """
    feedbacks = (
        db.query(ContentFeedback)
        # ContentFeedback이 video_id를 가지고 있으므로 Video 테이블과 조인
        .filter(ContentFeedback.user_id == user_id)
        .order_by(ContentFeedback.updated_at.desc())
        .all()
    )

    return [
        FeedbackResponse(
            titles=fb.titles,
            hashtags=fb.hashtags,
            similar_videos=[
                YoutubeTitleResponse(**sv) for sv in (fb.similar_videos or [])
            ],
        )
        for fb in feedbacks
    ]