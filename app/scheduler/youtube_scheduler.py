# app/scheduler/youtube_scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from app.services.youtube_service import crawl_and_store
from app.db.session import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
scheduler = BlockingScheduler()

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
    scheduler.add_job(
        youtube_job,
        trigger='cron',
        day_of_week='mon',
        hour=3,
        minute=0,
        id='weekly_youtube_crawl',
        replace_existing=True
    )
    logging.info("[Scheduler] YouTube 스케줄러 시작")
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()
