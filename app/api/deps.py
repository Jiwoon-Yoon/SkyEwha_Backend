# app/api/deps.py
from app.db.session import SessionLocal
from typing import Generator

def get_db()->Generator:
    # SessionLocal()을 호출하여 데이터베이스와의 세션을 생성
    db= SessionLocal()
    try:
        # yield를 사용해 생성된 세션 객체를 반환
        # FastAPI 라우트에서 사용자가 데이터베이스 작업을 수행할 수 있도록 세션을 제공
        yield db
    finally:
        # 작업이 끝난 후 세션을 닫아 데이터베이스 리소스를 해제
        db.close()