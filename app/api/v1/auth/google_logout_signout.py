#app/api/v1/auth/google_logout_signout.py
from fastapi import APIRouter, HTTPException, status, Depends
import httpx
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user_token
from app.schemas.auth import GoogleLogoutResponse, GoogleUnlinkResponse
from app.models import user
from app.services.google_service import (
    get_google_access_token,
    delete_google_access_token,
    delete_user_google_data,
)

router = APIRouter()

# ========================================
# 구글 로그아웃: access token 폐기
# ========================================
@router.post("/google/logout", summary="구글 로그아웃", response_model=GoogleLogoutResponse)
async def logout_google(current_user: dict = Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    구글 access token을 revoke(폐기)하고, user_is_active를 False로 설정 (앱에서 로그아웃 상태)
    """
    try:
        # 현재 로그인한 유저의 user_id를 토큰에서 추출
        user_id = current_user["user_id"]

        # DB에서 해당 유저의 구글 access_token 가져오기
        google_access_token = await get_google_access_token(user_id)
        print(f"token: {google_access_token}")  # None이면 실패

        google_logout_success = False

        if google_access_token:
            try:
                async with httpx.AsyncClient() as client:
                    # 구글은 별도 로그아웃 API는 없고, revoke로 access_token을 폐기함
                    response = await client.post(
                        "https://oauth2.googleapis.com/revoke",
                        data={"token": google_access_token},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )

                # 응답 코드 200 → 폐기 성공
                if response.status_code == 200:
                    google_logout_success = True

                    # redis 토큰 삭제
                    await delete_google_access_token(user_id)

                    # 유저 정보 조회해서 user_is_active = False로 설정
                    user_obj = db.query(user.User).filter(user.User.user_id == user_id).first()
                    if user_obj:
                        user_obj.user_is_active = False
                        db.commit()
                    print("구글 로그아웃 성공 - 토큰 폐기 완료")
                else:
                    print(f"구글 로그아웃 실패: {response.status_code} - {response.text}")
            except httpx.RequestError as e:
                print(f"구글 로그아웃 요청 실패: {e}")

        return GoogleLogoutResponse(
            message="구글 로그아웃이 완료되었습니다" if google_logout_success else "구글 로그아웃 중 오류 발생",
            success=True,
            google_logout_success=google_logout_success
        )

    except Exception as e:
        # 서버 내부 에러 처리
        raise HTTPException(status_code=500, detail=f"구글 로그아웃 실패: {str(e)}")


# ========================================
# 구글 연결 해제 (회원탈퇴)
# ========================================
@router.post("/google/unlink", summary="구글 계정 연결 해제", response_model=GoogleUnlinkResponse)
async def unlink_google(current_user: dict = Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    구글 access token을 revoke(폐기)한 후 DB에서 사용자 데이터 삭제
    """
    try:
        user_id = current_user["user_id"]

        #DB에서 access_token 조회
        google_access_token = await get_google_access_token(user_id)

        google_unlink_success = False

        if google_access_token:
            try:
                # 연결 해제는 revoke 후 DB 정리로 처리
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://oauth2.googleapis.com/revoke",
                        params={"token": google_access_token},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )

                # revoke 성공 시
                if response.status_code == 200:
                    google_unlink_success = True
                    print("구글 연결 해제 성공 - 토큰 폐기 완료")

                    # 토큰 정보 및 사용자 데이터 DB에서 제거
                    await delete_google_access_token(user_id)
                    await delete_user_google_data(user_id, db)

                else:
                    print(f"구글 연결 해제 실패: {response.status_code} - {response.text}")

            except httpx.RequestError as e:
                print(f"구글 연결 해제 요청 실패: {e}")

        return GoogleUnlinkResponse(
            message="구글 연결 해제가 완료되었습니다" if google_unlink_success else "구글 연결 해제 실패",
            success=True,
            google_unlink_success=google_unlink_success
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"구글 연결 해제 실패: {str(e)}")