# app/api/auth/token.py
from fastapi import APIRouter
from app.services.kakao_service import set_kakao_access_token
from app.schemas.auth import GoogleTokenSaveRequest
from app.services.google_service import set_google_access_token

router = APIRouter()

@router.post("/token")
async def save_token(user_id: str, token: str):
    success = await set_kakao_access_token(user_id, token)
    return {"success": success}

# 구글 토큰 저장
@router.post("/google")
async def save_google_token(data: GoogleTokenSaveRequest):
    success = await set_google_access_token(data.user_id, data.access_token)
    return {"success": success}