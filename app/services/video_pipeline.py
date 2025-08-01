# app/services/video_pipeline.py
import os
from app.services.whisper_service import transcribe_audio
from app.services.keyword_service import extract_keywords, parse_keywords, send_keywords
from app.core.config import settings
from sqlalchemy.orm import Session

def process_video_for_keywords(db: Session, user_id: int, video_title: str, video_id: int):
    filename = f"{user_id}_{video_title}.mp4"  # 확장자 필요 시 더 안전하게 처리 가능
    file_path = os.path.join(settings.upload_dir, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"비디오 파일을 찾을 수 없습니다: {file_path}")

    print("음성 → 텍스트 변환 시작")
    text = transcribe_audio(file_path)

    print("추출된 텍스트:\n", text)

    print("키워드 생성 중...")
    raw_keywords = extract_keywords(text)

    print("키워드 결과:")
    print(raw_keywords)

    parsed_keywords = parse_keywords(raw_keywords)

    print("키워드 전송 중...")
    send_keywords(db, video_id, parsed_keywords)

    # 마지막에 로컬에서 영상 삭제
    try:
        os.remove(file_path)
        print(f"파일 삭제 완료: {file_path}")
    except Exception as e:
        print(f"파일 삭제 중 오류 발생: {e}")
