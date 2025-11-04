from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.keyword import WhisperProcessRequest, TextProcessRequest
from app.services.video_pipeline import process_video_for_keywords
from app.services.text_pipeline import process_text_for_keywords
from app.crud.crud_video import get_video_by_id
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/process_video_keywords/")
def process_video_keywords(
    request: WhisperProcessRequest,
    db: Session = Depends(deps.get_db),
):
    video = get_video_by_id(db, video_id= request.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # video.user_id, video.video_title 정보로 키워드 처리 호출
    feedback= process_video_for_keywords(
        db=db,
        user_id=video.user_id,
        video_title=video.video_title,
        video_id=video.video_id,
    )

    if not feedback:
        raise HTTPException(status_code=500, detail="키워드 분석 결과를 저장하지 못했습니다.")

    return {
        "message": "키워드 처리 완료",
        "feedback_id": feedback.feedback_id
     }


@router.post("/process_text_keywords/")
def process_text_keywords(
        request: TextProcessRequest,  # 새로운 텍스트 스키마 사용
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(get_current_user),):
    # video_id 대신 input_text와 text_title을 service 함수에 전달
    try:
        feedback = process_text_for_keywords(
            db=db,
            user_id = current_user.user_id,
            input_text=request.input_text,
            text_title=request.text_title,
        )
        if not feedback:
            raise HTTPException(status_code=500, detail="키워드 분석 결과를 저장하지 못했습니다.")

    except Exception as e:
        # 서비스 레이어에서 발생한 오류 처리
        print(f"텍스트 키워드 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"텍스트 키워드 처리 중 오류가 발생했습니다: {e}")

    return {
        "message": "텍스트 키워드 처리 완료",
        "feedback_id": feedback.feedback_id
    }

