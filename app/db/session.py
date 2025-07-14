# app/db/session.py
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = settings.DATABASE_URL
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)
