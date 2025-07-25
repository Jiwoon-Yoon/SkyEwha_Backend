# app/db/base.py
from sqlalchemy.ext.declarative import  declarative_base

Base = declarative_base()

# 여기에 모든 모델 import
from app.models.user import User
from app.models.video import Video
from app.models.keyword import Keyword
from app.models.youtube import YouTubeVideo