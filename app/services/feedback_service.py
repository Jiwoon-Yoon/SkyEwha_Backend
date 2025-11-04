# app/services/feedback_service.py
from sqlalchemy.orm import Session
from app.services.title_generation import generate_title_from_keywords
from app.services.hashtag_service import recommend_hashtags_from_keywords
from app.crud import crud_keyword
from app.crud.crud_youtube import get_videos_by_keywords_similarity
from app.schemas.youtube import YoutubeTitleResponse

def recommend_titles(db: Session, feedback_id: int) -> list[str]:
    return generate_title_from_keywords(db, feedback_id)

def recommend_hashtags(db: Session, feedback_id: int, top_n: int = 10) -> list[str]:
    return recommend_hashtags_from_keywords(db, feedback_id, top_n=top_n)

def recommend_similar_videos(db: Session, feedback_id: int, limit: int = 10) -> list[YoutubeTitleResponse]:
    keywords = crud_keyword.get_keywords_by_feedback_id(db, feedback_id)
    if not keywords:
        return []
    videos_with_scores = get_videos_by_keywords_similarity(db, keywords, limit=limit)
    return [
        YoutubeTitleResponse(
            title=vid.title,
            video_url=vid.video_url,
            thumbnail_url=vid.thumbnail_url,
            published_at=vid.published_at,
            similarity=score,
        )
        for vid, score in videos_with_scores
    ]
