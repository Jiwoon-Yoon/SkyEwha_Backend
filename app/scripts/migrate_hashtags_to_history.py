# app/scripts/migrate_hashtags_to_history.py
from sqlalchemy.orm import Session
from app.models.hashtag import Hashtag
from app.models.hashtag_history import HashtagHistory
from app.db.session import SessionLocal

# 이 코드는 1회용
def migrate_hashtags_to_history():
    db: Session = SessionLocal()
    try:
        hashtags = db.query(Hashtag).all()
        for h in hashtags:
            history = HashtagHistory(
                hashtag=h.hashtag,
                week_posts=h.week_posts,
                collected_at=h.last_updated
            )
            db.add(history)
        db.commit()
        print(f"{len(hashtags)} hashtags migrated to history.")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_hashtags_to_history()
