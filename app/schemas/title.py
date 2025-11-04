# app/schemas/title.py
from pydantic import BaseModel

class TitleRequest(BaseModel):
    feedback_id: int

class TitleResponse(BaseModel):
    titles: list[str]