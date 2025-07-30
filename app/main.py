# app/main.py
from fastapi import FastAPI
from app.api.v1.routers import api_router
from contextlib import asynccontextmanager
from app.scheduler.youtube_scheduler import scheduler, start_scheduler

@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}

app.include_router(api_router)
