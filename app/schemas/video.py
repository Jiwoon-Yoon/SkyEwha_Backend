# app/schemas/video.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class VideoBase(BaseModel):
    video_title: str

class VideoCreate(VideoBase):
    # user_id와 upload_date는 서버에서 처리 (입력 X)
    pass

class Video(VideoBase):
    video_id: int
    user_id: int
    upload_date: date

    class Config:
        orm_mode = True
