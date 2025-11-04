#app/schemas/content_feedback.py
from pydantic import BaseModel
from typing import Optional, List

class ContentFeedbackBase(BaseModel):
    """ContentFeedback 모델의 기본 필드를 정의합니다."""
    source_type: str  # 'video' 또는 'text'
    source_title: str # 영상 제목 또는 텍스트 제목
    video_id: Optional[int] = None
    input_text: Optional[str] = None # 텍스트 원본 (저장하지 않기로 결정했으므로, NULL 허용)


class ContentFeedbackCreate(ContentFeedbackBase):
    # 생성 시에는 ContentFeedbackBase의 필드만 사용합니다.
    pass

class ContentFeedbackUpdate(BaseModel):
    """AI 분석 결과를 ContentFeedback 레코드에 업데이트할 때 사용되는 스키마입니다."""
    titles: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    similar_videos: Optional[List[int]] = None