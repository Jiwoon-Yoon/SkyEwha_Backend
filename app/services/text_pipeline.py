# app/services/text_pipeline.py
from app.services.keyword_service import extract_keywords, parse_keywords, send_keywords
from sqlalchemy.orm import Session
from app.crud.crud_content_feedback import create_content_feedback
from app.schemas.content_feedback import ContentFeedbackCreate

def process_text_for_keywords(db: Session, user_id: int, input_text: str, text_title: str):
    # 1. feedback_id를 발급받아 키워드 저장을 위한 식별자로 사용합니다.
    feedback_in = ContentFeedbackCreate(
        source_type="text",
        source_title=text_title,
        video_id=None,
        input_text=None,  # 원본 텍스트 저장을 안 하기로 했으므로 NULL
    )
    feedback_record = create_content_feedback(db, user_id=user_id, feedback_in=feedback_in)
    feedback_id = feedback_record.feedback_id

    # 2. 키워드 생성 (extract_keywords 재활용)
    print("키워드 생성 중...")
    # NOTE: video_pipeline에서 transcribe_audio 대신 input_text를 바로 사용
    raw_keywords = extract_keywords(input_text)

    print("키워드 결과:")
    print(raw_keywords)

    # 3. 키워드 파싱 (parse_keywords 재활용)
    parsed_keywords = parse_keywords(raw_keywords)

    # 4. 키워드 전송 및 임베딩 저장 (send_keywords 재활용)
    # send_keywords 함수를 feedback_id를 받도록 수정해야 합니다.
    print("키워드 전송 중...")
    # video_id 대신 feedback_id를 넘겨줍니다.
    send_keywords(db, feedback_id, parsed_keywords)

    return feedback_record