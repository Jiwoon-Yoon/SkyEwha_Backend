import re
from pathlib import Path
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer, util

# 임베딩 모델 로드 (전역으로 한 번만)
model = SentenceTransformer('all-MiniLM-L6-v2')

# 기준 문장 리스트 (여행 관련 키워드/문장)
travel_reference_texts = [
    "여행", "관광", "휴가", "브이로그", "트립", "여행지 소개", "호텔", "맛집", "비행기", "패키지 여행",
    "캠핑", "등산", "휴양지", "관광 명소", "자연 풍경", "여행 코스", "문화 체험"
]

# 기준 문장 임베딩 미리 계산
reference_embeddings = model.encode(travel_reference_texts, convert_to_tensor=True)

def extract_hashtags(desc):
    return re.findall(r"#(\w+)", desc.lower())

def is_excluded_video(title, description):
    exclude_keywords = {'mv', 'music', '광고', 'promo', 'review', '뮤직비디오', 'official', '뉴스', 'news', 'ebs', '교육', '방송', 'kbs', 'mbc', 'sbs'}
    text = (title + " " + description).lower()
    return any(word in text for word in exclude_keywords)

def is_travel_video(text, threshold=0.5):
    try:
        video_embedding = model.encode(text, convert_to_tensor=True)
        cosine_scores = util.cos_sim(video_embedding, reference_embeddings)
        max_score = cosine_scores.max().item()
        return max_score >= threshold, max_score
    except Exception as e:
        print(f"[ERROR] is_travel_video failed: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"is_travel_video failed: {e}")
