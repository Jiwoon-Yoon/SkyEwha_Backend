# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserNicknameUpdate
from typing import Optional


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    주어진 user_id로 데이터베이스에서 사용자 정보를 조회합니다.
    """
    return db.query(User).filter(User.user_id == user_id).first()


def update_user_nickname(db: Session, user: User, new_nickname: str) -> User:
    """
    특정 사용자의 닉네임을 업데이트하고 변경 사항을 커밋합니다.
    닉네임 중복 검사는 요청 사항에 따라 생략합니다.
    """
    # 닉네임 업데이트
    user.user_nickname = new_nickname

    # 데이터베이스에 변경 사항을 커밋합니다.
    db.add(user)
    db.commit()
    db.refresh(user)  # 변경된 내용을 반영하여 객체를 새로 고칩니다.

    return user
