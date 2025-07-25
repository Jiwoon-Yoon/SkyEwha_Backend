# app/api/v1/auth/kakao_logout_signout.py
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
import httpx
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import get_current_user_token
from app.schemas.auth import KakaoLogoutResponse, KakaoUnlinkResponse
from app.models import user
from app.services.kakao_service import get_kakao_access_token, delete_kakao_access_token, delete_user_kakao_data

router = APIRouter()

@router.post("/kakao/logout",
             summary="카카오계정과 함께 로그아웃 (카카오 로그아웃 + 계정 세션 만료)",
             description="카카오 세션을 종료하고 애플리케이션 토큰도 무효화",
             response_model=KakaoLogoutResponse)
async def logout_kakao(current_user: dict = Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    카카오 계정과 함께 로그아웃 (카카오 로그아웃 URL 생성)
    프론트엔드는 이 URL로 redirect하면 됨.
    swagger에서 테스트 시 authorize에 Bearer {access_token} 입력
    """
    try:
        user_id = current_user["user_id"]

        # Redis에서 사용자의 카카오 액세스 토큰 가져오기
        kakao_access_token = await get_kakao_access_token(user_id)
        print(f"kakao_access_token: {kakao_access_token}")  # None이면 실패

        kakao_logout_success = False

        kakao_logout_url = (
            f"{settings.kakao_logout}"
            f"?client_id={settings.kakao_client_id}"
            f"&logout_redirect_uri={settings.kakao_logout_redirect_url}"
        )


        # Redis에서 카카오 관련 토큰들 삭제 / user_is_active = False로
        try:
            await delete_kakao_access_token(user_id)
            user_obj = db.query(user.User).filter(user.User.user_id == user_id).first()
            if user_obj:
                user_obj.user_is_active = False
                db.commit()
            print(f"Redis에서 카카오 토큰 삭제 완료 - 사용자 ID: {user_id}")

        except Exception as redis_error:
            print(f"Redis 토큰 삭제 실패: {redis_error}")

        return KakaoLogoutResponse(
            message="카카오 로그아웃 URL이 생성되었습니다. 이 URL로 리다이렉트하세요.",
            success=True,
            kakao_logout_success=True,
            kakao_logout_url=kakao_logout_url  # 프론트엔드에서 이 URL로 리다이렉트
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카카오 로그아웃 실패: {str(e)}"
        )



@router.post("/kakao/unlink",
             summary="카카오 어드민 키를 통한 회원탈퇴",
             description="카카오 계정과의 연결을 완전히 끊음 (회원탈퇴)",
             response_model=KakaoUnlinkResponse)
async def unlink_kakao(current_user: dict = Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    카카오 연결 해제 (회원탈퇴)
    - 카카오 계정과의 연결을 완전히 끊음
    """
    # 사용자 정보 가져오기
    user_id = current_user["user_id"]
    user_obj = db.query(user.User).filter(user.User.user_id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    # 연결 해제 요청용: 카카오 사용자 ID
    kakao_user_id = user_obj.user_social_id
    if not kakao_user_id:
        raise HTTPException(status_code=400, detail="카카오 사용자 ID가 없습니다")

    try:
        # 어드민 키 방식 unlink 요청
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.kakao_unlink,
                headers={
                    "Authorization": f"KakaoAK {settings.kakao_admin_key}",
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                },
                data={
                    "target_id_type": "user_id",
                    "target_id": kakao_user_id
                }
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"카카오 unlink 실패: {response.text}"
            )

        # Redis에서 사용자 정보 삭제 또는 카카오 연결 정보 삭제
        await delete_kakao_access_token(user_id)
        await delete_user_kakao_data(user_id, db)
        return {
            "success": True,
            "message": f"사용자 {user_id} 의 카카오 연결이 해제되고 탈퇴 처리되었습니다.",
            "kakao_unlink_success": True
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"카카오 연결 해제 중 오류 발생: {str(e)}"
        )

