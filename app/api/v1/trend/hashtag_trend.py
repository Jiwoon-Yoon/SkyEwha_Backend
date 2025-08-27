# app/api/v1/trend/hashtag_trend.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.hashtag_history import HashtagHistory
from app.crud.crud_hashtag_history import get_rising_hashtags
from app.crud.crud_hashtag import get_best_hashtags

router = APIRouter()

@router.get("/hashtag")
def weekly_trend_report(db: Session = Depends(deps.get_db)):
    # hashtag_history 테이블에서 최근 2개의 수집 날짜 가져오기
    recent_dates = (
        db.query(HashtagHistory.collected_at)
        .distinct()
        .order_by(HashtagHistory.collected_at.desc())
        .limit(2)
        .all()
    )

    if len(recent_dates) < 2:
        raise HTTPException(status_code=400, detail="데이터가 최소 2개 필요합니다.")

    this_week_date = recent_dates[0][0]  # 가장 최근 수집일
    last_week_date = recent_dates[1][0]  # 그 전 수집일

    # today = date.today()
    # this_week_date = today - timedelta(days=today.weekday())  # 이번 주 월요일
    # last_week_date = this_week_date - timedelta(days=7)        # 지난 주 월요일

    best = get_best_hashtags(db, top_n=10)
    rising = get_rising_hashtags(db, this_week_date, last_week_date, top_n=10)

    return {
        "best_hashtags": best,
        "rising_hashtags": rising,
    }