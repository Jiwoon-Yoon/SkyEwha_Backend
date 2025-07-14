# app/api/auth/token.py
from fastapi import APIRouter
from app.services.kakao_service import set_kakao_access_token

router = APIRouter()

@router.post("/token")
async def save_token(user_id: str, token: str):
    success = await set_kakao_access_token(user_id, token)
    return {"success": success}