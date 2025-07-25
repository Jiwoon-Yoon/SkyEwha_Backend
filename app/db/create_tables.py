#app/db/create_tables.py
from app.db.base import Base
from app.db.session import engine
import app.models  # 모델들이 임포트되어야 Base.metadata에 등록됨

Base.metadata.create_all(bind=engine)
print("테이블 생성 완료")