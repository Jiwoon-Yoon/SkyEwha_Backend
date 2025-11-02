# app/schemas/user.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 닉네임 변경 요청 시 사용할 Pydantic 모델
class UserNicknameUpdate(BaseModel):
    """닉네임 업데이트를 위한 요청 스키마"""
    user_nickname: str = Field(..., min_length=1, max_length=10, description="변경된 사용자 닉네임")

    class Config:
        # 데이터베이스의 ORM 객체에서 필드를 읽을 수 있도록 설정
        from_attributes = True

# 사용자 응답 (닉네임 변경 후 결과를 보여주기 위함)
class UserResponse(BaseModel):
    """사용자 정보를 클라이언트에 반환하기 위한 응답 스키마"""
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_nickname: str
    user_provider: str
    created_at: datetime
    user_is_active: bool
    user_last_login: Optional[datetime] = None

    class Config:
        from_attributes = True