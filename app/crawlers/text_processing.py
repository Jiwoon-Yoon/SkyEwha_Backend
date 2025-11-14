#app/crawlers/text_processing.py
import re
import numpy as np
import joblib
from fastapi import HTTPException
from openai import OpenAI

from app.core.config import settings

api_key = settings.openai_api_key
if not api_key:
    raise ValueError("OPENAI_API_KEY를 .env 파일에 설정해 주세요.")

client = OpenAI(api_key=api_key)

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

def extract_hashtags(desc):
    """해시태그 추출"""
    return re.findall(r"#(\w+)", desc.lower())

# -----------------------------
#  학습된 분류 모델 로드
# -----------------------------
try:
    # 프로젝트 루트 기준으로 model_store/travel_classifier.joblib 에 있다고 가정
    TRAVEL_MODEL = joblib.load("model_store/travel_classifier.joblib")
    print("[INFO] travel_classifier 모델 로드 완료")
except Exception as e:
    print(f"[WARN] travel_classifier 로드 실패: {e}", flush=True)
    TRAVEL_MODEL = None

def is_travel_video(text: str, threshold: float = 0.5):
    """
    학습된 분류 모델 기반 여행 영상 여부 판별

    - text: 보통 "title + description" 합친 문자열
    - return: (is_travel: bool, prob_travel: float)
    """
    if TRAVEL_MODEL is None:
        raise HTTPException(status_code=500, detail="Travel classifier model not loaded")

    try:
        if not isinstance(text, str):
            text = "" if text is None else str(text)

        emb = get_embedding(text)
        emb = np.array(emb, dtype=np.float32).reshape(1, -1)

        # predict_proba → [[p(non-travel), p(travel)]]
        prob_travel = float(TRAVEL_MODEL.predict_proba(emb)[0][1])
        is_travel = prob_travel >= threshold

        return is_travel, prob_travel

    except Exception as e:
        print(f"[ERROR] is_travel_video failed: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"is_travel_video failed: {e}")