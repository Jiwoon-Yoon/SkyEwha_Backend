from datetime import datetime, timedelta
from dateutil import parser
from fastapi import HTTPException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session
from app.schemas.youtube import YoutubeVideoCreate
from app.core.config import settings
from app.crud.crud_youtube import save_videos_to_db

# 임포트 추가
from app.crawlers.text_processing import (
    extract_hashtags,
    #is_excluded_video,
    is_travel_video,
)

YOUTUBE_API_KEY = settings.youtube_api_key
REGION_CODE = settings.region_code
MAX_RESULTS = settings.max_results

def fetch_youtube_video_ids(keyword='여행'):
    """
        유튜브 검색 API를 사용해 특정 키워드로 최근 90일 내에 올라온 영상 ID 리스트를 가져온다.
        Args:
            keyword (str): 검색어, 기본값은 '여행'
        Returns:
            video_id 리스트 (str)
        Raises:
            HTTPException: API 호출 실패 시 500 에러 반환
    """
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        published_after = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ')
        search_response = youtube.search().list(
            q=keyword,
            part='id',
            regionCode=REGION_CODE,
            maxResults=MAX_RESULTS,
            type='video',
            order='viewCount',
            publishedAfter=published_after
        ).execute()
        return [item['id']['videoId'] for item in search_response.get('items', [])]
    except Exception as e:
        print(f"[fetch_youtube_video_ids] ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"fetch_youtube_video_ids failed: {e}")

def fetch_video_details(video_ids):
    """
    영상 ID 리스트를 받아서 상세 정보를 API로 조회하고, 여행 영상 여부 판별 후 리스트로 반환한다.
    Args:
        video_ids (List[str]): 유튜브 영상 ID 리스트
    Returns:
        여행 영상 정보 딕셔너리 리스트
    Raises:
        HTTPException: 유튜브 API 호출 실패 또는 형식 오류 시 에러 발생
    """
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

            # # 제외 영상 체크
            # if is_excluded_video(title, description):
            #     continue

            # 임베딩 기반 여행 영상 판별
            is_travel, score = is_travel_video(full_text)
            if not is_travel:
                continue

            hashtags = extract_hashtags(description)

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
                "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                "travel_score": score,  # 참고용 점수 포함 가능
            })

        return results

    except HttpError:
        raise HTTPException(status_code=502, detail="Failed to fetch videos from YouTube API")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

def crawl_and_store(keyword: str, db: Session) -> int:
    """
    주어진 키워드로 유튜브 영상들을 크롤링하고, 여행 영상으로 판별된 영상만 DB에 저장한다.
    Args:
        keyword (str): 유튜브 검색 키워드
        db (Session): SQLAlchemy DB 세션
    Returns:
        저장된 여행 영상 개수 (int)
    Raises:
        HTTPException: 내부 처리 중 에러 발생 시 예외 던짐
    """
    try:
        video_ids = fetch_youtube_video_ids(keyword)
        videos_data = fetch_video_details(video_ids)
        videos = [YoutubeVideoCreate(**video) for video in videos_data]
        save_videos_to_db(videos, db)
        return len(videos)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
