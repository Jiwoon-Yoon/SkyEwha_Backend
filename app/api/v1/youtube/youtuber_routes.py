from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.youtube_service import get_uploads_playlist, fetch_all_videos, store_videos
import time
import logging
import traceback

router = APIRouter()

# uvicorn 로거 사용
logger = logging.getLogger("uvicorn")

channel_ids = [
    "UCgDlijNPh7yHQNv0YdL11fQ",
    "UClRNDVO8093rmRTtLe4GEPw",
    "UCNhofiqfw5nl-NeDJkXtPvw",
    "UCnGrAY8_VaXFYw3Y1p-6Lfw",
    "UC9gxOp_-R78phMHmv2bW_sg"
]

@router.post("/crawl_channels")
def crawl_channels(db: Session = Depends(get_db)):
    total_saved = 0

    for cid in channel_ids:
        try:
            logger.info(f"===== 채널 {cid} 수집 시작 =====")

            playlist_id = get_uploads_playlist(cid)
            logger.info(f"playlist_id: {playlist_id}")

            videos = fetch_all_videos(playlist_id)
            logger.info(f"총 {len(videos)}개 영상 가져옴")
            if videos:
                logger.info(f"첫 번째 영상 예시: {videos[0]}")

            saved_count = store_videos(videos, db)
            logger.info(f"✅ 채널 {cid}에서 {saved_count}개 저장 완료\n")
            total_saved += saved_count

        except Exception as e:
            logger.error(f"⚠ Failed to process channel {cid}: {e}")
            logger.error(traceback.format_exc())
            continue

        # API quota 방지
        time.sleep(0.2)

    logger.info(f"🎯 총 저장된 영상: {total_saved}개")
    return {"message": f"{total_saved}개의 채널 영상이 DB에 저장되었습니다."}
