from sqlalchemy.orm import Session
from app.models.video_feedback import VideoFeedback
from app.schemas.feedback import FeedbackResponse


def get_feedback_by_video_id(db: Session, video_id: int) -> VideoFeedback | None:
    """
    video_id로 VideoFeedback 조회
    """
    return db.query(VideoFeedback).filter(VideoFeedback.video_id == video_id).first()


def upsert_feedback(db: Session, video_id: int, feedback: FeedbackResponse) -> VideoFeedback:
    """
    1:1 관계 피드백을 upsert
    - 존재하면 업데이트
    - 없으면 새로 생성
    """
    db_feedback = get_feedback_by_video_id(db, video_id)

    if db_feedback:
        # 기존 레코드 업데이트
        db_feedback.titles = feedback.titles
        db_feedback.hashtags = feedback.hashtags
        db_feedback.similar_videos = [sv.dict() for sv in feedback.similar_videos]
    else:
        # 새 레코드 생성
        db_feedback = VideoFeedback(
            video_id=video_id,
            titles=feedback.titles,
            hashtags=feedback.hashtags,
            similar_videos=[sv.dict() for sv in feedback.similar_videos]
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
