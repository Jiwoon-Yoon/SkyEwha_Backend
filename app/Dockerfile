# app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 필수 패키지 설치 (git, ffmpeg, 빌드 도구)
RUN apt-get update && \
    apt-get install -y --fix-missing -o Acquire::Retries=3 git ffmpeg build-essential && \
    rm -rf /var/lib/apt/lists/*


# requirements 먼저 복사
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#COPY . .
# FastAPI 앱 복사
COPY ./app ./app

CMD ["gunicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
