from sqlalchemy.orm import Session
from datetime import datetime
from app.models.video_feedback import VideoFeedback
from app.schemas.feedback import FeedbackResponse

def get_feedback_by_video_id(db: Session, video_id: int) -> VideoFeedback | None:
    """
    video_id로 VideoFeedback 조회
    """
    return db.query(VideoFeedback).filter(VideoFeedback.video_id == video_id).first()


def upsert_feedback(db: Session, video_id: int, feedback: FeedbackResponse) -> VideoFeedback:
    """
    VideoFeedback을 upsert
    - 존재하면 업데이트
    - 없으면 새로 생성
    - Pydantic 2.x model_dump() 사용
    - datetime 변환 없이 JSON 컬럼 저장
    """
    db_feedback = get_feedback_by_video_id(db, video_id)

    # JSON 컬럼 저장용 직렬화
    similar_videos_serializable = [
        {
            **sv.model_dump(),
            "published_at": sv.published_at.isoformat() if sv.published_at else None
        }
        for sv in feedback.similar_videos
    ]

    if db_feedback:
        # 기존 레코드 업데이트
        db_feedback.titles = feedback.titles
        db_feedback.hashtags = feedback.hashtags
        db_feedback.similar_videos = similar_videos_serializable
        db_feedback.updated_at = datetime.now()
    else:
        # 새 레코드 생성
        db_feedback = VideoFeedback(
            video_id=video_id,
            titles=feedback.titles,
            hashtags=feedback.hashtags,
            similar_videos=similar_videos_serializable,
            updated_at=datetime.now()
        )
        db.add(db_feedback)

    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def delete_feedback(db: Session, video_id: int) -> bool:
    """
    video_id 기반으로 피드백 삭제
    """
    db_feedback = get_feedback_by_video_id(db, video_id)
    if not db_feedback:
        return False
    db.delete(db_feedback)
    db.commit()
    return True
