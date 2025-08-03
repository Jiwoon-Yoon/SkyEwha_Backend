# app/api/v1/routers.py
from fastapi import APIRouter
from app.api.v1.auth import kakao_auth
from app.api.v1.auth import kakao_logout_signout
from app.api.v1.auth import google_auth
from app.api.v1.auth import google_logout_signout
from app.api.v1.auth import token
from app.api.v1.youtube import youtube_routes
from app.api.v1 import upload_video
from app.api.v1 import keyword_generater
from app.api.v1 import feedback

api_router = APIRouter()
api_router.include_router(kakao_auth.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(kakao_logout_signout.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(token.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(google_auth.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(google_logout_signout.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(youtube_routes.router, prefix="/api/v1/youtube", tags=["YouTube"])
api_router.include_router(upload_video.router, prefix="/api/v1/video", tags=["Video"])
api_router.include_router(keyword_generater.router, prefix="/api/v1/keyword", tags=["Keyword"])
api_router.include_router(feedback.router, prefix="/api/v1/title", tags=["Title"])