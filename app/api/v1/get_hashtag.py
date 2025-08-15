# app/api/v1/get_hashtag.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.hashtag import HashtagCreate, HashtagInDB
from app.crud.crud_hashtag import update_or_create_hashtag
from sqlalchemy.orm import Session
from app.api import deps

router = APIRouter()

@router.post("/hashtags/", response_model=HashtagInDB)
async def create_hashtag(
    hashtag: HashtagCreate,
    db: Session = Depends(deps.get_db)
):
    obj, action = update_or_create_hashtag(
        db=db,
        hashtag_str=hashtag.hashtag,
        week_posts=hashtag.week_posts
    )
    return HashtagInDB.model_validate(obj)
