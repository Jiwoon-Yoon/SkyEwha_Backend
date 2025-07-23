# app/main.py
from fastapi import FastAPI
from app.api.v1.routers import api_router

app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}

app.include_router(api_router)
