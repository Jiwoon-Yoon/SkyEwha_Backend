#app/api/v1/youtube/youtube_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.youtube_service import crawl_and_store

router = APIRouter()

@router.post("/crawl", summary="유튜브에서 여행 영상을 데이터 불러와 DB에 저장")
def crawl_youtube(keyword: str = "여행", db: Session = Depends(get_db)):
    """유튜브에서 여행 영상 수집 및 DB 저장"""
    count = crawl_and_store(keyword, db)
    return {"message": f"{count}개의 여행 영상이 저장되었습니다."}
