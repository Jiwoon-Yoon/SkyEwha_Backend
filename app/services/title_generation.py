from openai import OpenAI
from app.crud import crud_keyword
from sqlalchemy.orm import Session
from app.core.config import settings
import re

api_key = settings.openai_api_key
if not api_key:
    raise ValueError("OPENAI_API_KEY를 .env 파일에 설정해 주세요.")

client = OpenAI(api_key=api_key)
def generate_title_from_keywords(db: Session, feedback_id: int) -> list[str]:
    """
    200만 구독자 여행 유튜버를 위한
    키워드 기반 맞춤형 클릭률 높은 영상 제목 후보 3~5개 생성
    """
    keywords = crud_keyword.get_keywords_by_feedback_id(db, feedback_id)
    keyword_str = ", ".join(keywords)
    prompt = f"""
당신은 200만 구독자를 보유한 여행 유튜버를 위한 영상 제목 전문가입니다.

아래 키워드를 참고하여, 클릭률을 높일 수 있는 매력적인 유튜브 숏폼 제목 후보 3~5개를 추천해주세요.
- 제목은 15~30자 이내로 작성해주세요.
- 한국어로 작성해주세요.
- 제목은 리스트 형태로 출력해주세요.
- 제목과 어울리는 이모지도 포함해서 작성해주세요.

키워드: {keyword_str}
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )
    text = response.choices[0].message.content.strip()
    titles = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return titles