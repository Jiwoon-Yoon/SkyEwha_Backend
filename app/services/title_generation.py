from openai import OpenAI
from app.crud import crud_keyword
from sqlalchemy.orm import Session
from app.core.config import settings
import json

api_key = settings.openai_api_key
if not api_key:
    raise ValueError("OPENAI_API_KEY를 .env 파일에 설정해 주세요.")

client = OpenAI(api_key=api_key)

def generate_title_from_keywords(db: Session, feedback_id: int) -> list[str]:
    keywords = crud_keyword.get_keywords_by_feedback_id(db, feedback_id)
    keyword_str = ", ".join(keywords)

    prompt = f"""
당신은 200만 구독자를 보유한 여행 유튜버를 위한 영상 제목 전문가입니다.

아래 키워드를 참고하여, 클릭률을 높일 수 있는 매력적인 유튜브 숏폼 제목 후보 3~5개를 생성해주세요.

조건:
- 제목은 15~30자 이내
- 한국어
- 이모지 포함
- 설명 절대 금지
- 번호 절대 금지
- **JSON 배열 형식으로만 출력** (중요)
- 예: ["제목1 😊", "제목2 🍁", "제목3 ✨"]

키워드: {keyword_str}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 안정적인 모델 추천
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )

    raw = response.choices[0].message.content

    print("==== RAW MODEL TEXT ====")
    print(repr(raw))
    print("finish_reason:", response.choices[0].finish_reason)

    # GPT가 반드시 JSON 배열만 반환하도록 했기 때문에 파싱도 단순함
    try:
        titles = json.loads(raw)
    except:
        # 혹시 GPT가 실수하면 강제로 다시 요청하거나 fallback 처리할 수도 있음
        titles = []

    return titles
