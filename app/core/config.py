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

    class Config:
        env_file = ".env"

settings = Settings()