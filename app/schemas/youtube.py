#app/schemas/youtube.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional


# 1. 요청용 (ex: /crawl?keyword=여행)
class YoutubeCrawlRequest(BaseModel):
    keyword: str
    max_results: int


# 2. DB insert 용 (Service -> Model로 변환 시 사용)
class YoutubeVideoCreate(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    published_at: datetime
    channel_title: Optional[str]
    tags: Optional[List[str]]
    thumbnail_url: Optional[HttpUrl]
    video_url: Optional[HttpUrl]
    view_count: Optional[int] = 0


# 3. 응답용 (Model -> Client로 리턴 시 사용)
class YoutubeVideo(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    published_at: datetime
    channel_title: Optional[str]
    tags: Optional[List[str]]
    thumbnail_url: Optional[HttpUrl]
    video_url: Optional[HttpUrl]
    view_count: Optional[int] = 0
    created_at: datetime

class KeywordSearchRequest(BaseModel):
    keywords: List[str]

class YoutubeTitleResponse(BaseModel):
    video_id: str
    title: str
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    published_at: datetime
    similarity: float

class KeywordRecommendResponse(BaseModel):
    results: List[YoutubeTitleResponse]

class PopularVideo(BaseModel):
    video_id: str
    thumbnail_url: HttpUrl

class PopularVideosResponse(BaseModel):
    results: List[PopularVideo]