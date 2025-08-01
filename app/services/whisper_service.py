# app/services/whisper_service.py
import whisper

_model = None  # 전역 모델 캐싱

def load_whisper_model(model_size="medium"):
    global _model
    if _model is None:
        print("Whisper 모델 로드 중...")
        _model = whisper.load_model(model_size)
    return _model

def transcribe_audio(file_path: str, language="Korean") -> str:
    model = load_whisper_model()
    result = model.transcribe(file_path, language=language)
    return result["text"]
