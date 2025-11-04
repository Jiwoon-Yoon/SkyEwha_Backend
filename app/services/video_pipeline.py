# app/services/video_pipeline.py
import os
from app.services.whisper_service import transcribe_audio
from app.services.keyword_service import extract_keywords, parse_keywords, send_keywords
from app.core.config import settings
from sqlalchemy.orm import Session
from typing import Optional
from app.models.content_feedback import ContentFeedback
from app.schemas.content_feedback import ContentFeedbackCreate, ContentFeedbackUpdate
from app.crud.crud_content_feedback import create_content_feedback

def process_video_for_keywords(db: Session, user_id: int, video_title: str, video_id: int)-> Optional[ContentFeedback]:
    filename = f"{user_id}_{video_title}.mp4"  # 확장자 필요 시 더 안전하게 처리 가능
    file_path = os.path.join(settings.upload_dir, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"비디오 파일을 찾을 수 없습니다: {file_path}")

    # 1. ContentFeedback 레코드 생성 (빈 레코드)
    # video_title을 source_title로 사용하여 feedback_id를 발급받습니다.
    feedback_in = ContentFeedbackCreate(
        source_type="video",
        source_title=video_title,
        video_id=video_id,
        input_text=None,
    )
    feedback_record = create_content_feedback(db, user_id=user_id, feedback_in=feedback_in)
    feedback_id = feedback_record.feedback_id

    print("음성 → 텍스트 변환 시작")
    # OpenAI API (빠름, 유료)
    text = transcribe_audio(file_path, backend="openai")

    # 로컬 Whisper (무료, CPU 환경은 "small" 권장)
    # text = transcribe_audio(file_path, backend="local")

    print("추출된 텍스트:\n", text)

    print("키워드 생성 중...")
    raw_keywords = extract_keywords(text)

    print("키워드 결과:")
    print(raw_keywords)

    parsed_keywords = parse_keywords(raw_keywords)

    print("키워드 전송 중...")
    send_keywords(db, feedback_id, parsed_keywords)

    # 마지막에 로컬에서 영상 삭제
    try:
        os.remove(file_path)
        print(f"파일 삭제 완료: {file_path}")
    except Exception as e:
        print(f"파일 삭제 중 오류 발생: {e}")

    return feedback_record
