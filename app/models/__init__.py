# app/models/__init__.py
# 앞으로 다른 모델 생기면 여기 계속 추가
from .user import User
from app.db.base import Base

from app.db.session import engine

Base.metadata.create_all(engine)
print("테이블 생성 완료")