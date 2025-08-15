#app/crawlers/text_processing.py
import re
import numpy as np
from fastapi import HTTPException
from openai import OpenAI

from app.core.config import settings

api_key = settings.openai_api_key
if not api_key:
    raise ValueError("OPENAI_API_KEY를 .env 파일에 설정해 주세요.")

client = OpenAI(api_key=api_key)

# 기준 문장 리스트 (여행 관련 키워드/문장)
travel_reference_texts = [
    "여행", "관광", "휴가", "브이로그", "트립", "여행지 소개", "호텔", "맛집", "비행기", "패키지 여행",
    "캠핑", "등산", "휴양지", "관광 명소", "자연 풍경", "여행 코스", "문화 체험"
]

def get_embedding(text: str, model: str = "text-embedding-3-small"):
    """OpenAI 임베딩 생성"""
    try:
        resp = client.embeddings.create(
            model=model,
            input=text
        )
        return resp.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI embedding failed: {e}")

# 기준 문장 임베딩 미리 계산
reference_embeddings = [get_embedding(t) for t in travel_reference_texts]

def cosine_similarity(vec_a, vec_b):
    """코사인 유사도 계산"""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def extract_hashtags(desc):
    """해시태그 추출"""
    return re.findall(r"#(\w+)", desc.lower())

# def is_excluded_video(title, description):
#     """여행 관련 영상에서 제외할 키워드"""
#     exclude_keywords = {
#         'mv', 'music', '광고', 'promo', 'review', '뮤직비디오', 'official',
#         '뉴스', 'news', 'ebs', '교육', '방송', 'kbs', 'mbc', 'sbs'
#     }
#     text = (title + " " + description).lower()
#     return any(word in text for word in exclude_keywords)

def is_travel_video(text, threshold=0.3):
    """여행 영상 여부 판별"""
    try:
        video_embedding = get_embedding(text)
        max_score = max(
            cosine_similarity(video_embedding, ref)
            for ref in reference_embeddings
        )
        return max_score >= threshold, max_score
    except Exception as e:
        print(f"[ERROR] is_travel_video failed: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"is_travel_video failed: {e}")
