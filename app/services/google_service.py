# app/services/google_service.py
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
import redis.asyncio as redis
from app.core.config import settings

# Redis 클라이언트 설정
redis_client = redis.Redis(host=settings.redis_host, port=6379, db=0, decode_responses=True)


async def get_google_access_token(user_id: str) -> Optional[str]:
    """사용자의 구글 액세스 토큰을 Redis에서 조회합니다."""
    try:
        token = await redis_client.get(f"google_access:{user_id}")
        return token if token else None
    except redis.RedisError:
        return None


async def set_google_access_token(user_id: str, access_token: str, expire_hours: int = 6) -> bool:
    """사용자의 구글 액세스 토큰을 Redis에 저장합니다."""
    try:
        print(f"set_google_access_token 호출됨: user_id={user_id}, token={access_token[:10]}...")
        await redis_client.setex(
            f"google_access:{user_id}",
            expire_hours * 3600,
            access_token
        )
        return True
    except redis.RedisError as e:
        print("Redis error:", e)
        return False


async def delete_google_access_token(user_id: str) -> bool:
    """사용자의 구글 액세스 토큰을 Redis에서 삭제합니다."""
    try:
        result = await redis_client.delete(f"google_access:{user_id}")
        return result > 0
    except redis.RedisError:
        return False


async def get_user_by_id(user_id: str, db: Session) -> Optional[User]:
    """사용자 ID로 사용자를 조회합니다."""
    return db.query(User).filter(User.user_id == user_id).first()


async def delete_user_google_data(user_id: str, db: Session) -> bool:
    """사용자의 구글 관련 데이터를 모두 삭제합니다 (회원탈퇴용)."""
    # Redis에서 토큰 삭제
    token_deleted = await delete_google_access_token(user_id)

    # DB에서 사용자 삭제
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True

    return token_deleted