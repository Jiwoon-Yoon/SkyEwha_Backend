# app/core/auth.py
# get_current_user_token 함수 옮기기
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.security import get_current_user_token
from app.models.user import User

def get_current_user(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user_token)
) -> User:
    user_id = token_data["user_id"]

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user