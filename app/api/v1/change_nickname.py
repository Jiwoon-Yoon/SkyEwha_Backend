# app/api/v1/change_nickname.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserNicknameUpdate, UserResponse
from app.models.user import User
from app.crud.crud_user import get_user_by_id, update_user_nickname

router = APIRouter()

@router.patch(
    "/users/{user_id}/nickname",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="사용자 닉네임 변경",
    description="주어진 ID의 사용자의 닉네임을 업데이트합니다. 닉네임 중복은 허용됩니다."
)
async def update_nickname(
        user_id: int,
        nickname_in: UserNicknameUpdate,
        db: Session = Depends(get_db),
        # 실제 환경에서는 get_current_user를 통해 인증된 사용자만 접근하도록 제한합니다. 권한 검사 시 추가
        # 예: current_user: User = Depends(get_current_user),
):
    """
    특정 사용자의 닉네임을 변경하는 엔드포인트입니다.
    """

    # 1. 대상 사용자 조회
    user = get_user_by_id(db, user_id)
    if not user:
        # 사용자가 존재하지 않는 경우 404 에러 반환
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # 2. 닉네임 업데이트 실행
    updated_user = update_user_nickname(db, user=user, new_nickname=nickname_in.user_nickname)

    # 3. 업데이트된 사용자 정보 반환
    return updated_user
