# update_view_counts.py
from googleapiclient.discovery import build
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models.youtube import YouTubeVideo
from app.core.config import settings

YOUTUBE_API_KEY = settings.youtube_api_key
DATABASE_URL = settings.DATABASE_URL  # SQLAlchemy DB URL

# DB 세션 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


def update_view_counts():
    video_ids = [v.video_id for v in db.query(YouTubeVideo.video_id).all()]
    chunk_size = 50

    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i + chunk_size]
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = youtube.videos().list(
            part="statistics",
            id=",".join(chunk)
        ).execute()

        for item in response.get("items", []):
            video = db.query(YouTubeVideo).filter(YouTubeVideo.video_id == item["id"]).first()
            if video:
                video.view_count = int(item.get("statistics", {}).get("viewCount", 0))

    db.commit()
    print(f"총 {len(video_ids)}개의 조회수를 업데이트했습니다.")


if __name__ == "__main__":
    update_view_counts()
    db.close()
