#app/services/youtube_service.py
from datetime import datetime, timedelta
from dateutil import parser
from fastapi import HTTPException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.crud_youtube import save_videos_to_db
from app.crawlers.text_processing import (
    extract_mixed_keywords,
    extract_hashtags,
    is_excluded_video,
    is_travel_related
)

YOUTUBE_API_KEY = settings.youtube_api_key
REGION_CODE = settings.region_code
MAX_RESULTS = settings.max_results

def fetch_youtube_video_ids(keyword='여행'):
    print(f"[fetch_youtube_video_ids] keyword: {keyword}")
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        published_after = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"published_after: {published_after}")
        search_response = youtube.search().list(
            q=keyword,
            part='id',
            regionCode=REGION_CODE,
            maxResults=MAX_RESULTS,
            type='video',
            order='viewCount',
            publishedAfter=published_after
        ).execute()
        print(f"API Response Items: {len(search_response.get('items', []))}")
        return [item['id']['videoId'] for item in search_response.get('items', [])]
    except Exception as e:
        print(f"[fetch_youtube_video_ids] ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"fetch_youtube_video_ids failed: {e}")

def fetch_video_details(video_ids):
    if not video_ids:
        return []

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        videos_response = youtube.videos().list(
            part="snippet",
            id=','.join(video_ids)
        ).execute()

        results = []
        for item in videos_response.get('items', []):
            title = item['snippet']['title']
            description = item['snippet'].get('description', '')
            full_text = f"{title} {description}"

            keywords = extract_mixed_keywords(full_text)
            hashtags = extract_hashtags(description)

            if is_excluded_video(title, description):
                continue
            if not is_travel_related(keywords, hashtags):
                continue

            try:
                published_at = parser.isoparse(item['snippet']['publishedAt'])
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid publishedAt format for video {item['id']}")

            results.append({
                "video_id": item['id'],
                "title": title,
                "description": description,
                "published_at": published_at,
                "channel_title": item['snippet']['channelTitle'],
                "tags": hashtags,
                "thumbnail_url": item['snippet']['thumbnails']['high']['url'],
                "video_url": f"https://www.youtube.com/watch?v={item['id']}"
            })

        return results

    except HttpError:
        raise HTTPException(status_code=502, detail="Failed to fetch videos from YouTube API")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

def crawl_and_store(keyword: str, db: Session) -> int:
    """
    YouTube 영상 크롤링 후 여행 영상만 DB에 저장.
    """
    try:
        print(f"crawl_and_store 시작 - keyword: {keyword}")
        video_ids = fetch_youtube_video_ids(keyword)
        videos = fetch_video_details(video_ids)
        save_videos_to_db(videos, db)
        return len(videos)
    except HTTPException:
        # 이미 위 함수에서 처리한 HTTPException은 그대로 다시 던짐
        raise
    except Exception as e:
        # 여기서 원인 로그 출력 또는 에러 메시지 포함해 반환
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

