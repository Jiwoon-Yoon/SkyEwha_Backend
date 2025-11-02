# app/crud/crud_hashtag_history.py
from sqlalchemy.orm import Session
from app.models.hashtag_history import HashtagHistory
from datetime import date
from typing import List, Dict
from app.models.hashtag import Hashtag

def get_latest_week(db: Session) -> date:
    """가장 최근 수집 주차 날짜 반환"""
    latest = db.query(HashtagHistory.collected_at).order_by(HashtagHistory.collected_at.desc()).first()
    return latest[0] if latest else None

def get_prev_week(db: Session, current_week: date) -> date:
    """현재 주차 이전 주차 날짜 반환"""
    prev = db.query(HashtagHistory.collected_at)\
             .filter(HashtagHistory.collected_at < current_week)\
             .order_by(HashtagHistory.collected_at.desc())\
             .first()
    return prev[0] if prev else None

def get_rising_hashtags(db: Session, this_week_date, last_week_date, top_n: int = 10):
    # 활성화된 해시태그의 히스토리만 필터링하는 쿼리 빌더
    base_query = db.query(HashtagHistory).join(
        Hashtag, Hashtag.hashtag == HashtagHistory.hashtag
    ).filter(
        Hashtag.is_active == True  # <--- 활성화 필터 추가
    )

    # 이번 주 데이터
    this_week = (
        base_query
        .filter(HashtagHistory.collected_at == this_week_date)
        .all()
    )
    # 지난 주 데이터
    last_week = (
        base_query
        .filter(HashtagHistory.collected_at == last_week_date)
        .all()
    )

    last_week_dict = {h.hashtag: h.week_posts for h in last_week}

    rising_list = []
    for h in this_week:
        last_val = last_week_dict.get(h.hashtag, 0)
        diff = h.week_posts - last_val
        growth_rate = round((diff / (last_val + 1)) * 100, 2)

        rising_list.append({
            "hashtag": h.hashtag,
            "this_week": h.week_posts,
            "growth_rate": growth_rate,
        })

    # 증가율 기준 정렬
    rising_list.sort(key=lambda x: x["growth_rate"], reverse=True)
    return rising_list[:top_n]
