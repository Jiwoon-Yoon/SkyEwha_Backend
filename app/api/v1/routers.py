# app/api/v1/routers.py
from fastapi import APIRouter
from app.api.v1.auth import kakao_auth
from app.api.v1.auth import kakao_logout_signout
from app.api.v1.auth import google_auth
from app.api.v1.auth import google_logout_signout
from app.api.v1.auth import token

api_router = APIRouter()
api_router.include_router(kakao_auth.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(kakao_logout_signout.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(token.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(google_auth.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(google_logout_signout.router, prefix="/api/v1/auth", tags=["Social Auth"])