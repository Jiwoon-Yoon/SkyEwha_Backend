# app/crud/crud_hashtag.py
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.hashtag import Hashtag
from app.services.embedding_service import get_embedding
import numpy as np
import datetime
from app.models.hashtag_history import HashtagHistory

def calculate_view_weight(week_posts: int, total_posts: int) -> float:
    return round((week_posts / (total_posts + 1)) + np.log1p(week_posts), 4)

def update_or_create_hashtag(db: Session, hashtag_str: str, week_posts: int):
    """
        embedding: Optional, numpy array or list 형태 (벡터 임베딩)
    """

    db_hashtag = db.query(Hashtag).filter(Hashtag.hashtag == hashtag_str).first()
    now = datetime.date.today()

    if db_hashtag:
        new_total = (db_hashtag.total_posts or 0) + week_posts
        db_hashtag.week_posts = week_posts
        db_hashtag.total_posts = new_total
        view_weight = float(calculate_view_weight(week_posts, new_total))
        db_hashtag.view_weight = view_weight
        db_hashtag.last_updated = now

        db.add(db_hashtag)
        db.commit()
        db.refresh(db_hashtag)

        # history에도 저장
        history = HashtagHistory(
            hashtag=hashtag_str,
            week_posts=week_posts,
            collected_at=now
        )
        db.add(history)
        db.commit()

        return db_hashtag, "updated"
    else:
        embedding = get_embedding(hashtag_str)  # OpenAI 호출

        new_hashtag = Hashtag(
            hashtag=hashtag_str,
            week_posts=week_posts,
            total_posts=week_posts,
            view_weight=float(calculate_view_weight(week_posts, week_posts)),
            last_updated=now,
            embedding= embedding,
            is_active = True
        )
        db.add(new_hashtag)
        db.commit()
        db.refresh(new_hashtag)

        # history에도 저장
        history = HashtagHistory(
            hashtag=hashtag_str,
            week_posts=week_posts,
            collected_at=now
        )
        db.add(history)
        db.commit()

        return new_hashtag, "created"

def get_best_hashtags(db: Session, top_n: int = 10):
    hashtags = (
        db.query(Hashtag)
        .filter(Hashtag.total_posts != None)
        .filter(Hashtag.is_active == True)
        .order_by(Hashtag.total_posts.desc())
        .limit(top_n)
        .all()
    )
    return [
        {
            "hashtag": h.hashtag,
            "total_posts": h.total_posts,
        }
        for h in hashtags
    ]
