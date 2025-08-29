#app/api/v1/youtube/youtube_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.youtube_service import crawl_and_store
from app.schemas.youtube import KeywordSearchRequest, KeywordRecommendResponse, YoutubeTitleResponse, \
    PopularVideosResponse
from app.crud.crud_youtube import get_videos_by_keywords_similarity, get_top_videos_by_views

router = APIRouter()

@router.post("/crawl", summary="유튜브에서 여행 영상을 데이터 불러와 DB에 저장")
def crawl_youtube(keyword: str = "여행", db: Session = Depends(get_db)):
    """유튜브에서 여행 영상 수집 및 DB 저장"""
    try:
        count = crawl_and_store(keyword, db)
        return {"message": f"{count}개의 여행 영상이 저장되었습니다."}
    except Exception as e:
        import traceback
        traceback.print_exc()  # 전체 에러 스택 출력
        raise e  # 필요하면 다시 에러 올림

@router.post("/presearch", response_model=KeywordRecommendResponse)
def keyword_search(
    request: KeywordSearchRequest,
    db: Session = Depends(get_db)
):
    if not request.keywords:
        raise HTTPException(status_code=400, detail="키워드를 입력해주세요.")

    try:
        videos_with_scores = get_videos_by_keywords_similarity(db, request.keywords, limit=10)

        # → videos_with_scores: List[Tuple[YouTubeVideo, float]]
        results = [
            YoutubeTitleResponse(
                title=video.title,
                video_url=video.video_url,
                thumbnail_url=video.thumbnail_url,
                published_at=video.published_at,
                similarity=score
            )
            for video, score in videos_with_scores
        ]

        return KeywordRecommendResponse(results=results)
    except Exception as e:
        import traceback
        traceback.print_exc()  # 전체 에러 스택 출력
        raise e  # 필요하면 다시 에러 올림


@router.get(
    "/popular",
    summary="조회수 기준 인기 영상 Top 3",
    response_model=PopularVideosResponse
)
def get_popular_videos(db: Session = Depends(get_db)):
    """
    조회수 기준으로 인기 영상 Top 3의 썸네일 URL만 반환합니다.
    """
    try:
        thumbnails = get_top_videos_by_views(db, limit=3)

        if not thumbnails:
            raise HTTPException(
                status_code=404,
                detail="인기 영상을 찾을 수 없습니다."
            )

        return PopularVideosResponse(thumbnails=thumbnails)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류: {str(e)}"
        )
