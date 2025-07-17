# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel

class KakaoTokenRequest(BaseModel):
    code: str

class GoogleTokenRequest(BaseModel):
    code: str

class GoogleTokenSaveRequest(BaseModel):
    user_id: str
    access_token: str

class CompleteSignupRequest(BaseModel):
    nickname: str
    temp_token: str
    name: Optional[str] = None
    email: Optional[str] = None
    access_token: Optional[str] = None  # Optional로 둬서 필요할 때만 전달

class KakaoLogoutResponse(BaseModel):
    message: str
    success: bool
    kakao_logout_success: bool

class KakaoUnlinkResponse(BaseModel):
    message: str
    success: bool
    kakao_unlink_success: bool

class GoogleLogoutResponse(BaseModel):
    message: str
    success: bool
    google_logout_success: bool

class GoogleUnlinkResponse(BaseModel):
    message: str
    success: bool
    google_unlink_success: bool
