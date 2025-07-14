# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL : str
    kakao_token_url : str
    kakao_userInfo_url : str
    kakao_client_id : str
    kakao_redirect_url : str
    kakao_auth_url : str
    kakao_secret : str
    jwt_secret_key : str

    class Config:
        env_file = ".env"

settings = Settings()