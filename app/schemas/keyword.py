# app/schemas/keyword.py
from pydantic import BaseModel
from typing import List

class WhisperProcessRequest(BaseModel):
    video_id: int

class KeywordCreate(BaseModel):
    feedback_id: int
    keyword: str
    embedding: list[float] | None = None

# 텍스트 입력을 위한 스키마
class TextProcessRequest(BaseModel):
    input_text: str  # 사용자가 직접 입력한 텍스트 내용
    text_title: str  # 텍스트 분석 결과의 제목 (필수)