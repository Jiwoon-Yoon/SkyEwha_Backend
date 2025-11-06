# app/api/v1/routers.py
from fastapi import APIRouter
from app.api.v1.auth import kakao_auth, kakao_logout_signout, google_auth, google_logout_signout, token
from app.api.v1.youtube import youtube_routes, youtuber_routes
from app.api.v1 import upload_video, keyword_generater, get_hashtag,change_nickname,bookmark_routes
from app.api.v1.feedback import hashtag_feedback, title_feedback, feedback_route
from app.api.v1.trend import hashtag_trend

api_router = APIRouter()
api_router.include_router(kakao_auth.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(kakao_logout_signout.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(token.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(google_auth.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(google_logout_signout.router, prefix="/api/v1/auth", tags=["Social Auth"])
api_router.include_router(youtube_routes.router, prefix="/api/v1/youtube", tags=["YouTube"])
api_router.include_router(upload_video.router, prefix="/api/v1/video", tags=["Video"])
api_router.include_router(keyword_generater.router, prefix="/api/v1/keyword", tags=["Keyword"])
api_router.include_router(title_feedback.router, prefix="/api/v1/title", tags=["Title"])
api_router.include_router(get_hashtag.router, prefix="/api/v1/hashtag", tags=["Hashtag"])
api_router.include_router(hashtag_feedback.router,prefix="/api/v1/recommend_hashtags", tags=["Hashtag"])
api_router.include_router(feedback_route.router, prefix="/api/v1/feedback", tags=["feedback"])
api_router.include_router(hashtag_trend.router, prefix="/api/v1/weekly_trend",tags=["weekly_trend"])
api_router.include_router(youtuber_routes.router, prefix="/api/v1/youtube", tags=["YouTube"])
api_router.include_router(change_nickname.router, prefix="/api/v1/mypage", tags=["Mypage"])
api_router.include_router(bookmark_routes.router, prefix="/api/v1/bookmarks", tags=["Bookmarks"])