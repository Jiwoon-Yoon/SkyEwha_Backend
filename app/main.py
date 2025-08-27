# app/main.py
from fastapi import FastAPI
from app.api.v1.routers import api_router
from contextlib import asynccontextmanager
from app.scheduler.youtube_scheduler import scheduler, start_scheduler
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json
import os

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # ✅ openapi.json 자동 저장
    output_path = "openapi.json"
    if not os.path.exists(output_path):
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes
        )
        with open(output_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)
        print(f"✅ openapi.json 생성 완료 → {output_path}")
    start_scheduler()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()

#app = FastAPI(lifespan=lifespan)
app = FastAPI(openapi_version="3.0.2", lifespan=lifespan)

@app.get("/ping")
def ping():
    return {"message": "pong"}

app.include_router(api_router)
