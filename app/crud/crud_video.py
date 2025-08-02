# app/crud/crud_video.py
import datetime

from sqlalchemy.orm import Session
from app.models.video import Video
from app.schemas.video import VideoCreate

def create_video(db: Session, video_in: VideoCreate, user_id: int) -> Video:
    video_dict = video_in.model_dump() #video_in을 딕셔너리로 변환
    video_dict["upload_date"]= datetime.date.today()
    video_dict["user_id"]=user_id
    db_video = Video(**video_dict)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_video_by_id(db: Session, video_id: int) -> Video | None:
    return db.query(Video).filter(Video.video_id == video_id).first()
