# app/services/hashtag_service
from sqlalchemy.orm import Session
from typing import List
import numpy as np
from app.crud.crud_keyword import get_keywords_with_embeddings_by_feedback_id
from app.models.hashtag import Hashtag
from app.services.embedding_service import cosine_similarity


def recommend_hashtags_from_keywords(db: Session, feedback_id: int, top_n: int = 10) -> List[str]:
    # 1. feedback_id로 keyword + embedding 가져오기
    db_keywords = get_keywords_with_embeddings_by_feedback_id(db, feedback_id)
    if not db_keywords:
        return []

    keyword_embeddings = [kw.embedding for kw in db_keywords]
    avg_embedding = np.mean(keyword_embeddings, axis=0)

    # 2. DB에서 모든 hashtag embedding 가져오기
    hashtags = db.query(Hashtag).filter(
        Hashtag.embedding != None,
        Hashtag.is_active == True
    ).all()
    if not hashtags:
        return []

    # # 3. cosine similarity 계산
    # scored_hashtags = []
    # for h in hashtags:
    #     sim = cosine_similarity(avg_embedding, h.embedding)
    #     scored_hashtags.append((h.hashtag, sim))

    # 각 keyword별로 점수 계산 후 합산
    hashtag_scores = {h.hashtag: 0.0 for h in hashtags}
    for kw in db_keywords:
        for h in hashtags:
            sim = cosine_similarity(kw.embedding, h.embedding)
            hashtag_scores[h.hashtag] += sim  # 점수 합산

    scored_hashtags = sorted(hashtag_scores.items(), key=lambda x: x[1], reverse=True)

    # 4. 정렬 후 top_n 반환
    scored_hashtags.sort(key=lambda x: x[1], reverse=True)
    return [h for h, _ in scored_hashtags[:top_n]]