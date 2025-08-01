# app/services/keyword_service.py
from openai import OpenAI
from app.crud import crud_keyword
from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas.keyword import KeywordCreate
import re

api_key = settings.openai_api_key
if not api_key:
    raise ValueError("OPENAI_API_KEY를 .env 파일에 설정해 주세요.")

client = OpenAI(api_key=api_key)

def extract_keywords(text: str) -> str:
    prompt = f"""
당신은 콘텐츠 마케팅 전문가입니다.

다음 한국어 텍스트 내용을 기반으로, 여행 유튜브 영상 설명란에 넣을 수 있는 **해시태그**들을 생성해주세요.
- 각 해시태그는 1~3단어로 구성해주세요.
- "#"을 붙인 형식으로 리스트 형태로 반환해주세요.
- 너무 일반적인 단어 대신 이 영상의 주제와 관련된 구체적인 키워드를 사용해주세요.
- 한국인 여행 유튜버를 위한 서비스임을 고려해주세요.
- 한국어 텍스트 내용을 기반으로 한국 국내 여행이면 해시태그에 '(해당지역)+여행'이라는 키워드는 필수로 포함해주세요.
- 한국어 텍스트 내용을 기반으로 한국이 아닌 해외 여행이면 해시태그에 '(해당나라)+여행'과 '(해당도시)+여행'이라는 키워드는 필수로 포함해주세요.
- 만약 키워드를 리스트 형태로 반환하다가 중간에 응답 길이 제한에 걸리면, 해당 (#키워드)는 삭제하고 출력해주세요.

텍스트:
\"\"\"{text}\"\"\"
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()


def parse_keywords(text: str) -> list[str]:
    return [tag.strip() for tag in re.findall(r"#([^\s#\"'\[\],]+)", text)]


def send_keywords(db: Session, video_id: int, keywords: list[str]):
    for keyword in keywords:
        keyword_data = KeywordCreate(
            video_id= video_id,
            keyword= keyword,
            embedding= None  # 향후 Embedding 추가 가능
        )
        crud_keyword.create_keyword(db, keyword_data)
        print(f" 저장됨: {keyword}")

