# app/scheduler/youtube_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from app.services.youtube_service import crawl_and_store
from app.db.session import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
scheduler = BackgroundScheduler()

def youtube_job():
    db = SessionLocal()
    try:
        logging.info("[Scheduler] YouTube 크롤링 시작")
        count = crawl_and_store("여행", db)
        logging.info(f"[Scheduler] 저장된 영상 수: {count}")
    except Exception as e:
        logging.error(f"[Scheduler] 에러 발생: {e}")
    finally:
        db.close()

def start_scheduler():
    # 1주일에 한 번 월요일 오전 3시 실행
    scheduler.add_job(
        youtube_job,
        trigger='cron',
        day_of_week='mon',
        hour=3,
        minute=0,
        id='weekly_youtube_crawl',
        replace_existing=True
    )
