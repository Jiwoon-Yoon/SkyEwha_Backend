#app/api/v1/title_feedback.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.title import TitleRequest, TitleResponse
from app.services.title_generation import generate_title_from_keywords

router = APIRouter()
@router.post("/recommend", response_model=TitleResponse)
def recommend_title(
    request: TitleRequest,
    db: Session = Depends(deps.get_db)
):
    try:
        titles = generate_title_from_keywords(db, request.feedback_id)
        return {"titles": titles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"제목 생성 실패: {e}")