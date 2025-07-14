# app/api/v1/auth/kakao_logout_signout.py
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
import httpx
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user_token
from app.schemas.auth import KakaoLogoutResponse, KakaoUnlinkResponse
from app.models import user
from app.services.kakao_service import get_kakao_access_token, delete_kakao_access_token, delete_user_kakao_data

router = APIRouter()

@router.post("/logout/kakao",
             summary="카카오 로그아웃",
             description="카카오 세션을 종료하고 애플리케이션 토큰도 무효화",
             response_model=KakaoLogoutResponse)
async def logout_kakao(current_user: dict = Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    카카오 로그아웃
    - 카카오 세션을 종료하고 애플리케이션 토큰도 무효화
    """
    try:
        user_id = current_user["user_id"]

        # 데이터베이스에서 사용자의 카카오 액세스 토큰 가져오기
        kakao_access_token = await get_kakao_access_token(user_id)

        kakao_logout_success = False

        if kakao_access_token:
            try:
                # 카카오 로그아웃 API 호출
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://kapi.kakao.com/v1/user/logout",
                        headers={
                            "Authorization": f"Bearer {kakao_access_token}",
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                    )

                if response.status_code == 200:
                    kakao_logout_success = True
                    result = response.json()
                    user_obj = db.query(user.User).filter(user.User.user_id == user_id).first()
                    if user_obj:
                        user_obj.user_is_active = False
                        db.commit()
                    print(f"카카오 로그아웃 성공 - 로그아웃된 사용자 ID: {result.get('id')}")
                else:
                    print(f"카카오 로그아웃 실패: {response.status_code} - {response.text}")

            except httpx.RequestError as e:
                print(f"카카오 로그아웃 요청 실패: {e}")

        return KakaoLogoutResponse(
            message="카카오 로그아웃이 완료되었습니다" if kakao_logout_success else "카카오 로그아웃 처리 중 오류가 발생했습니다",
            success=True,
            kakao_logout_success=kakao_logout_success
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카카오 로그아웃 실패: {str(e)}"
        )



@router.post("/unlink/kakao",
             summary="카카오 연결 해제",
             description="카카오 계정과의 연결을 완전히 끊음 (회원탈퇴)",
             response_model=KakaoUnlinkResponse)
async def unlink_kakao(current_user: dict = Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    카카오 연결 해제 (회원탈퇴)
    - 카카오 계정과의 연결을 완전히 끊음
    """
    try:
        user_id = current_user["user_id"]

        # 데이터베이스에서 사용자의 카카오 액세스 토큰 가져오기
        kakao_access_token = await get_kakao_access_token(user_id)

        kakao_unlink_success = False

        if kakao_access_token:
            try:
                # 카카오 연결 해제 API 호출
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://kapi.kakao.com/v1/user/unlink",
                        headers={
                            "Authorization": f"Bearer {kakao_access_token}",
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                    )

                if response.status_code == 200:
                    kakao_unlink_success = True
                    result = response.json()
                    print(f"카카오 연결 해제 성공 - 연결 해제된 사용자 ID: {result.get('id')}")

                    # 데이터베이스에서 사용자 정보 삭제 또는 카카오 연결 정보 삭제
                    await delete_kakao_access_token(user_id)
                    await delete_user_kakao_data(user_id,db)

                else:
                    print(f"카카오 연결 해제 실패: {response.status_code} - {response.text}")

            except httpx.RequestError as e:
                print(f"카카오 연결 해제 요청 실패: {e}")

        return KakaoUnlinkResponse(
            message="카카오 연결 해제가 완료되었습니다" if kakao_unlink_success else "카카오 연결 해제 처리 중 오류가 발생했습니다",
            success=True,
            kakao_unlink_success=kakao_unlink_success
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카카오 연결 해제 실패: {str(e)}"
        )