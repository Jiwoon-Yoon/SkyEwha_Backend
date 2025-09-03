# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL : str
    kakao_token_url : str
    kakao_userInfo_url : str
    kakao_client_id : str
    kakao_login_redirect_url : str
    kakao_auth_url : str
    kakao_secret : str
    jwt_secret_key : str
    kakao_logout: str
    kakao_unlink: str
    kakao_logout_redirect_url: str
    kakao_admin_key: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_auth_url: str
    google_token_url: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    #REDIS_PASSWORD: str = None  # Optional

    youtube_api_key: str
    region_code : str
    max_results: int
    top_keywords: int
    travel_score_threshold: int

    upload_dir: str

    openai_api_key: str

    # .env 파일에 REDIS_HOST 변수가 없으면 'localhost'를 기본값으로 사용
    redis_host: str = "localhost"

    class Config:
        env_file = ".env"

settings = Settings()