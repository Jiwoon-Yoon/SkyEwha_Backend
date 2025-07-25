#app/crawlers/text_processing.py
import re
from pathlib import Path
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from app.core.config import settings
from fastapi import HTTPException


# 현재 파일 기준 경로 설정
BASE_DIR = Path(__file__).resolve().parent

# 파일 경로들
STOPWORDS_PATH = BASE_DIR / "stopwords_ko.txt"

# 형태소 분석기
okt = Okt()

#설정값
REGION_CODE = settings.region_code
MAX_RESULTS = settings.max_results
TOP_KEYWORDS = settings.top_keywords
TRAVEL_SCORE_THRESHOLD = settings.travel_score_threshold

# 파일 로딩 함수들
def load_list(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# 카테고리별 가중치 및 키워드 사전
CATEGORY_WEIGHTS = {"일반": 3, "지역": 2, "활동": 2, "교통": 2, "테마": 1, "영어": 1}
travel_keywords_by_category = {
    "일반": ['여행', '브이로그', '트립', '휴가', '투어', '출발', '여정', '경로', '코스', '루트'],
    "지역": ['제주', '제주도', '부산', '서울', '강릉', '여수', '전주', '속초', '포항', '춘천', '경주', '울릉도',
             '한강', '남산', '경복궁', '해운대', '명동', '도쿄', '오사카', '후쿠오카', '삿포로', '방콕',
             '다낭', '푸켓', '세부', '발리', '파리', '런던', '로마', '바르셀로나', '베네치아', '뉴욕', 'LA',
             '샌프란시스코', '토론토', '멕시코시티'],
    "활동": ['캠핑', '등산', '트레킹', '낚시', '서핑', '스노클링', '자전거', '스쿠버', '패러글라이딩'],
    "교통": ['기차여행', '렌트카', '자유여행', '패키지', '비행기', '비자', '항공권'],
    "테마": ['맛집', '숙소', '호텔', '게스트하우스', '시장', '야시장', '풍경', '문화', '자연', '전통',
             '온천', '휴양지', '리조트', '관광지', '유적지', '명소'],
    "영어": ['trip', 'travel', 'vlog', 'resort', 'island', 'adventure',
             'tour', 'hiking', 'camping', 'beach', 'flight', 'visa', 'ticket', 'hotel', 'local']
}

# 키워드-가중치 딕셔너리 생성 (소문자 통일)
travel_keyword_weights = {
    kw.lower(): CATEGORY_WEIGHTS[cat]
    for cat, kws in travel_keywords_by_category.items()
    for kw in kws
}

# 제외 키워드 목록 (직접 리스트로)
exclude_keywords = {'mv', 'music', '광고', 'promo', 'review', '뮤직비디오', 'official', '뉴스', 'news', 'ebs', '교육', '방송', 'kbs', 'mbc', 'sbs'}

# 데이터 로딩
korean_stopwords = set(load_list(STOPWORDS_PATH))

def tokenize(text):
    try:
        return [t for t in okt.nouns(text) if t not in korean_stopwords and len(t) > 1]
    except Exception as e:
        print(f"[ERROR] tokenize failed: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"tokenize failed: {e}")

def extract_mixed_keywords(text, top_n=TOP_KEYWORDS):
    try:
        korean_text = ' '.join(re.findall(r'[가-힣]+', text))
        english_text = ' '.join(re.findall(r'[a-zA-Z]+', text))

        ko_keywords = [t for t in okt.nouns(korean_text) if t not in korean_stopwords and len(t) > 1]

        en_keywords = []
        if english_text.strip():
            try:
                tfidf = TfidfVectorizer(stop_words='english')
                matrix = tfidf.fit_transform([english_text])
                scores = matrix.toarray().flatten()
                terms = tfidf.get_feature_names_out()
                top_indices = scores.argsort()[-top_n:][::-1]
                en_keywords = [terms[i] for i in top_indices if scores[i] > 0]
            except ValueError:
                pass
        return list(dict.fromkeys(ko_keywords + en_keywords))[:top_n] or ["키워드없음"]

    except Exception as e:
        print(f"[ERROR] extract_mixed_keywords failed: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"extract_mixed_keywords failed: {e}")

def extract_hashtags(desc):
    return re.findall(r"#(\w+)", desc.lower())

def is_excluded_video(title, description):
    text = (title + " " + description).lower()
    return any(word in text for word in exclude_keywords)

def calculate_travel_score(keywords, hashtags):
    score = 0
    for kw in keywords + hashtags:
        score += travel_keyword_weights.get(kw.lower(), 0)
    return score

def is_travel_related(keywords, hashtags, threshold=TRAVEL_SCORE_THRESHOLD):
    return calculate_travel_score(keywords, hashtags) >= threshold