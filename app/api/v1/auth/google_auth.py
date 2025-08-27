#app/api/v1/auth/google_auth.py
from fastapi import APIRouter
from sqlalchemy.orm import Session
import httpx
from app.api import deps
from app.schemas import auth
from app.models import user
from app.core.security import *
from app.services.google_service import set_google_access_token

router = APIRouter()

@router.get("/google/login_url")
def get_google_login_url():
    """
    Google OAuth2 로그인 URL 생성
    """
    url = (
        f"{settings.google_auth_url}"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return {"login_url": url}

@router.post("/google/login")
async def google_login(data: auth.GoogleTokenRequest, db: Session = Depends(deps.get_db)):
    """
    Google 인가 코드로 토큰 요청 및 로그인 처리
    """
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            settings.google_token_url,
            data={
                "code": data.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if token_response.status_code != 200:
            error_info = {
                "error": "Google 인증 실패",
                "status_code": token_response.status_code,
                "google_response": token_response.text,
                "request_data": {
                    "client_id": settings.google_client_id,
                    "redirect_uri": settings.google_redirect_uri,
                    "code": data.code[:20] + "..." if len(data.code) > 20 else data.code
                }
            }
            raise HTTPException(status_code=400, detail=error_info)

        #구글 인증 성공하면
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        print(access_token)
        refresh_token = token_json.get("refresh_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="access_token 없음")

        print("✅ 받은 access_token:", access_token)
        # 사용자 정보 가져오기
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Google 사용자 정보 요청 실패")

        user_info = user_response.json()
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")

        if not google_id:
            raise HTTPException(status_code=400, detail="Google 사용자 ID 없음")

        # 기존 사용자 확인
        existing_user = db.query(user.User).filter(
            user.User.user_social_id == google_id,
            user.User.user_provider == "google"
        ).first()

        if existing_user:
            # 기존 사용자: 마지막 로그인 시간 업데이트
            existing_user.user_last_login = datetime.now()
            existing_user.user_is_active = True
            db.commit()

            # Redis에 구글 OAuth access_token 저장 (6시간)
            success = await set_google_access_token(str(existing_user.user_id), access_token)
            print("✅ Redis 저장 성공 여부:", success)

            print("✅ 저장할 user_id:", existing_user.user_id)

            # 기존 사용자: 내 앱의 JWT 토큰 생성
            app_access_token = create_access_token(subject=str(existing_user.user_id))
            app_refresh_token = create_refresh_token(subject=str(existing_user.user_id))

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
        temp_token = create_temp_token(subject=f"temp_{google_id}")

        return {
            "isNewUser": True,
            "tempToken": temp_token,
            "email": email,
            "name": name,
            "google_access_token": access_token
        }

@router.post("/google/signup", summary="구글 회원가입", description="닉네임 입력 후 회원가입")
async def google_signup(data: auth.CompleteSignupRequest, db: Session = Depends(deps.get_db)):
    # 임시 토큰 검증
    temp_subject = verify_token(data.temp_token, token_type="temp")
    if not temp_subject.startswith("temp_"):
        raise HTTPException(status_code=400, detail="유효하지 않은 임시 토큰")

    google_id = temp_subject.replace("temp_", "")

    new_user = user.User(
        user_social_id=google_id,
        user_provider="google",
        user_name=data.name,
        user_email=data.email,
        user_nickname=data.nickname,
        user_is_active=True,
        user_last_login=datetime.now()
        # 기타 필드 추가 가능
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Redis에 access_token 저장
    print(f"저장할 access_token: {data.access_token}")
    success = await set_google_access_token(str(new_user.user_id), data.access_token)
    print(f"Redis 저장 성공 여부: {success}")

    # 정식 JWT 토큰 발급
    app_access_token = create_access_token(subject=str(new_user.user_id))
    app_refresh_token = create_refresh_token(subject=str(new_user.user_id))

    return {
        "accessToken": app_access_token,
        "refreshToken": app_refresh_token,
        "user": {
            "user_id": new_user.user_id,
            "nickname": new_user.user_nickname,
            "email": new_user.user_email
        }
    }