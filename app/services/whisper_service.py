# app/services/whisper_service.py
import os
#import whisper
import tempfile
import subprocess
from openai import OpenAI
from app.core.config import settings

_openai_client = OpenAI(api_key=settings.openai_api_key)
_local_model = None  # 전역 모델 캐싱


# def load_whisper_model(model_size="medium"):
#     global _local_model
#     if _local_model is None:
#         print("Whisper 모델 로드 중...")
#         _local_model = whisper.load_model(model_size)
#     return _local_model


def transcribe_audio(file_path: str, language="Korean", backend="openai") -> str:
    """
    오디오 파일을 텍스트로 변환
    backend="openai" -> OpenAI API 사용 (빠름, 유료)
    backend="local"  -> 로컬 Whisper 사용 (무료, CPU 환경은 small 이하 권장)
    """
    if backend == "openai":
        tmp_out_path = None
        try:
            # 임시 mp3 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_out:
                tmp_out_path = tmp_out.name

            # ffmpeg으로 오디오만 추출 (mp3)
            subprocess.run(
                ["ffmpeg", "-i", file_path, "-vn", "-acodec", "libmp3lame", tmp_out_path, "-y"],
                check=True
            )

            # OpenAI Whisper API 호출
            with open(tmp_out_path, "rb") as audio_file:
                transcript = _openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        finally:
            # 임시 파일 삭제
            if tmp_out_path and os.path.exists(tmp_out_path):
                os.remove(tmp_out_path)


    # elif backend == "local":
    #     model = load_whisper_model()
    #     result = model.transcribe(file_path, language=language)
    #     return result["text"]

    else:
        raise ValueError(f"지원하지 않는 backend: {backend}")
