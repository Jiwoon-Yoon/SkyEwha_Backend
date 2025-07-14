# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel

class KakaoTokenRequest(BaseModel):
    code: str


class CompleteSignupRequest(BaseModel):
    nickname: str
    temp_token: str
    name: Optional[str] = None
    email: Optional[str] = None

class KakaoLogoutResponse(BaseModel):
    message: str
    success: bool
    kakao_logout_success: bool

class KakaoUnlinkResponse(BaseModel):
    message: str
    success: bool
    kakao_unlink_success: bool