from fastapi import APIRouter, UploadFile, File, Form
from fastapi.params import Depends
from sqlalchemy.orm import Session
import os
from app.api import deps
from app.schemas.video import Video
from app.services.video_service import handle_video_upload
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter()

UPLOAD_DIR = "upload_videos"  # 로컬 임시 저장 경로
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_video/", response_model=Video)
def upload_video(
    file: UploadFile = File(...),
    video_title: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
):
    return handle_video_upload(db, file, video_title, user_id = current_user.user_id)