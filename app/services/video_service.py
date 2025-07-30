# app/services/video_service.py
import os
import shutil
from app.core.config import settings
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.schemas.video import VideoCreate
from app.crud import crud_video

UPLOAD_DIR = settings.upload_dir

def save_video_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True) # dir 생성
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer) # UploadFile 내용 로컬에 저장
    return file_path

def handle_video_upload(
    db: Session, file: UploadFile, video_title: str, user_id: int
):
    # 1. 파일 저장
    save_video_file(file)

    # 2. DB 저장
    video_data = VideoCreate(
        video_title=video_title,
    )

    return crud_video.create_video(db, video_data, user_id)
