# app/core/security.py
from datetime import datetime,timedelta, UTC
from app.core.config import settings
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.params import Depends

# Security scheme
security = HTTPBearer()

# JWT 설정
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# JWT 액세스 토큰 생성
def create_access_token(subject: str, expires_delta: timedelta = None):
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

# JWT 리프레시 토큰 생성
def create_refresh_token(subject: str):
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# JWT 토큰 검증
def verify_token(token: str, token_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 토큰 타입"
            )

        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail= "토큰에 사용자 정보가 없습니다"
            )

        return subject

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_temp_token(subject: str, expires_minutes: int = 10):
    """임시 토큰 생성 (회원가입 완료용)"""
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "temp"
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 로그아웃, 회원탈퇴 시 사용
def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자의 JWT 토큰을 가져오고 검증"""
    token = credentials.credentials
    if token.startswith("Bearer "):  # Bearer 접두어 제거
        token = token.replace("Bearer ", "", 1)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # python-jose를 사용한 JWT 토큰 검증
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        return {
            "token": token,
            "user_id": user_id,
            "payload": payload
        }

    except JWTError:
        raise credentials_exception