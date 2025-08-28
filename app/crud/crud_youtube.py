# app/crud/crud_youtube.py
from sqlalchemy.orm import Session
from sqlalchemy import select
import numpy as np
from typing import List
from datetime import datetime
from app.models.youtube import YouTubeVideo
from app.schemas.youtube import YoutubeVideoCreate
from app.crawlers.text_processing import get_embedding as get_openai_embedding


def save_videos_to_db(videos: List[YoutubeVideoCreate], db: Session) -> None:
    """
    유튜브 영상 리스트를 DB에 저장합니다.
    중복 영상(예: video_id가 같은 영상)은 저장하지 않습니다.
    """
    for video in videos:
        # 중복 체크
        existing = db.query(YouTubeVideo).filter(
            YouTubeVideo.video_id == video.video_id
        ).first()
        if existing:
            # created_at만 최신으로 갱신
            existing.created_at = datetime.now()
            continue

        # OpenAI embedding 사용
        embedding_vector = get_openai_embedding(video.title)

        db_video = YouTubeVideo(
            video_id=video.video_id,
            title=video.title,
            description=video.description,
            published_at=video.published_at,
            channel_title=video.channel_title,
            tags=video.tags if video.tags else None,
            thumbnail_url=str(video.thumbnail_url) if video.thumbnail_url else None,
            video_url=str(video.video_url) if video.video_url else None,
            view_count=video.view_count,
            embedding=embedding_vector
        )

        db.add(db_video)

    db.commit()

def get_embedding(keywords: List[str]) -> List[float]:
    """키워드 리스트를 받아 평균 임베딩 생성"""
    vectors = [get_openai_embedding(k) for k in keywords]
    avg_vector = np.mean(vectors, axis=0)
    return avg_vector.tolist()

def get_videos_by_keywords_similarity(db: Session, keywords: List[str], limit: int = 10):
    embedding = get_embedding(keywords)  # List[float]

    # <=> 연산자 기반으로 코사인 거리 계산 + label("similarity") 직접 지정, 코사인 거리가 작을수록 유사
    similarity = YouTubeVideo.embedding.cosine_distance(embedding).label("similarity")

    stmt = (
        select(YouTubeVideo, similarity)
        .where(YouTubeVideo.embedding.isnot(None))
        .where(similarity <= 0.6)  # 유사도가 너무 낮은 건 제거
        .order_by(similarity)
        .limit(limit)
    )

    results = db.execute(stmt).all()  # List[Tuple[YouTubeVideo, float]]
    return results


def get_top_videos_by_views(db: Session, limit: int = 3):
    """
    조회수 기준 인기 영상 가져오기
    """
    videos = (
        db.query(YouTubeVideo.thumbnail_url)
        .order_by(YouTubeVideo.view_count.desc())
        .limit(limit)
        .all()
    )
    # [(url1,), (url2,), (url3,)] 형태라서 리스트로 변환
    return [v[0] for v in videos if v[0] is not None]
