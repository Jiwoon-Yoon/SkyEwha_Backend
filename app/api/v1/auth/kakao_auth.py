#app/api/v1/auth/kakao_auth.py
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
import httpx
from app.core.config import settings
from app.schemas import auth
from app.api import deps
from app.models import user
from app.core.security import *
from datetime import datetime

from app.services.kakao_service import set_kakao_access_token

router = APIRouter()

@router.get("/kakao/login_url")
def get_kakao_login_url():
    """
    카카오 로그인 URL 생성
    """
    kakao_login_url = (
        f"{settings.kakao_auth_url}"
        f"?client_id={settings.kakao_client_id}"
        f"&redirect_uri={settings.kakao_login_redirect_url}"
        f"&response_type=code"
    )
    return {"login_url": kakao_login_url}

# 사용자가 login_url로 들어가 로그인을 진행하면 인가 코드가 발급
# 예시) http://localhost:3000/kakao-callback?code=abcdefg12345

# 1단계: 소셜 로그인 인증
# 인가 코드에 관한 리턴값을 통해 신규/기존 회원 구분
@router.post("/kakao/login")
async def kakao_login(data: auth.KakaoTokenRequest, db:Session = Depends(deps.get_db)):
    async with httpx.AsyncClient() as client:
        # 카카오 액세스 토큰 요청
        token_response = await client.post(
            settings.kakao_token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.kakao_client_id,
                "redirect_uri": settings.kakao_login_redirect_url,
                "code": data.code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        )

        if token_response.status_code != 200:
            # 여러 방법으로 에러 정보 제공
            error_info = {
                "error": "카카오 인증 실패",
                "status_code": token_response.status_code,
                "kakao_response": token_response.text,
                "request_data": {
                    "client_id": settings.kakao_client_id,
                    "redirect_uri": settings.kakao_login_redirect_url,
                    "code": data.code[:20] + "..." if len(data.code) > 20 else data.code
                }
            }

            raise HTTPException(status_code=400, detail=error_info)
            # raise HTTPException(status_code=400, detail="카카오 인증 실패")


        # 카카오 인증 성공하면
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="access_token 없음")

        # 카카오 사용자 정보 요청
        user_response = await client.get(
            settings.kakao_userInfo_url,
            headers={"Authorization":f"Bearer {access_token}"}
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="사용자 정보 요청 실패")

        # 사용자 정보 요청 성공하면
        # 사용자 정보 파싱
        user_info = user_response.json()
        kakao_id = user_info.get("id")
        kakao_id=str(kakao_id)

        # 카카오 계정 정보 추출
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        email = kakao_account.get("email")
        name = profile.get("name")

        if not kakao_id:
            raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회 실패")

        # db에서 사용자 존재 여부 확인
        existing_user = db.query(user.User).filter(
            user.User.user_social_id == kakao_id, user.User.user_provider == "kakao").first()

        if existing_user:
            # 기존 사용자: 마지막 로그인 시간 업데이트
            existing_user.user_last_login = datetime.now()
            existing_user.user_is_active = True
            db.commit()

            # Redis에 access_token 저장
            print(f"저장할 access_token: {access_token}")
            success = await set_kakao_access_token(str(existing_user.user_id), access_token)
            print(f"Redis 저장 성공 여부: {success}")

            # 기존 사용자: 내 앱의 JWT 토큰 생성
            app_access_token = create_access_token(subject=str(existing_user.user_id))
            app_refresh_token = create_refresh_token(subject=str(existing_user.user_id))

            # return값은 클라이언트로 보내는 응답
            return {
                "isNewUser": False,
                "accessToken": app_access_token,
                "refreshToken": app_refresh_token,
                "user": {
                    "user_id": existing_user.user_id,
                    "nickname": existing_user.user_nickname,
                    "email": existing_user.user_email
                }
            }
        # 신규 사용자: 임시 토큰 발급 (닉네임 입력 전용)
        temp_token = create_temp_token(subject=f"temp_{kakao_id}")

        # return값은 클라이언트로 보내는 응답
        return {
            "isNewUser": True,
            "tempToken": temp_token,
            "email": email,
            "name": name,
            "kakao_access_token": access_token
        }


# 2단계 닉네임 입력 후 회원가입 완료
@router.post("/kakao/signup", summary="카카오 회원가입", description="카카오 로그인 후 닉네임 입력")
async def kakao_signup(
        data: auth.CompleteSignupRequest, db: Session = Depends(deps.get_db)
):
    # 임시 토큰 검증
    temp_subject = verify_token(data.temp_token, token_type="temp")

    if not temp_subject.startswith("temp_"):
        raise HTTPException(status_code=400, detail="유효하지 않은 임시 토큰")

    kakao_id = temp_subject.replace("temp_", "")

    new_user = user.User(
        user_social_id= kakao_id,
        user_provider= "kakao",
        user_name= data.name,
        user_email= data.email,
        user_nickname=data.nickname,
        user_is_active=True,
        user_last_login=datetime.now()
        # 기타 필요한 필드들...
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Redis에 access_token 저장
    print(f"저장할 access_token: {data.access_token}")
    success = await set_kakao_access_token(str(new_user.user_id), data.access_token)
    print(f"Redis 저장 성공 여부: {success}")

    # 정식 JWT 토큰 발급
    app_access_token = create_access_token(subject=str(new_user.user_id))
    app_refresh_token = create_refresh_token(subject=str(new_user.user_id))

    # return값은 클라이언트로 보내는 응답
    return {
        "accessToken": app_access_token,
        "refreshToken": app_refresh_token,
        "user": {
            "user_id": new_user.user_id,
            "nickname": new_user.user_nickname,
            "email": new_user.user_email
        }
    }