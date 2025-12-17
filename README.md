# SkyEwha-Backend

Trendie의 백엔드 서버 레포지토리입니다. 이 서버는 **유튜브 트렌드 데이터 수집·저장**, **사용자 인증(JWT, Kakao/Google OAuth)**, **Whisper(STT) 기반 텍스트 추출**, **OpenAI Embedding 기반 분석/추천**, **키워드 검색**, **북마크** 등 Trendie 핵심 기능의 비즈니스 로직과 API를 담당합니다.

FastAPI, SQLAlchemy, PostgreSQL(pgvector), Redis, APScheduler, OpenAI API(Embedding/Whisper), YouTube Data API v3 등의 기술을 기반으로 구현되어 있습니다.

---

## ✨ 프로젝트 개요

Trendie는 **초보 여행 유튜버**를 위한 트렌드 기반 콘텐츠 제작 지원 서비스입니다.  
틱톡·유튜브 데이터를 분석해 **주간 여행 트렌드**를 제공하고, 사용자가 업로드할 영상(또는 텍스트)을 분석하여 **트렌드를 반영한 제목·해시태그·유사 인기 영상**을 추천함으로써 콘텐츠 기획과 업로드 품질을 높일 수 있도록 돕습니다.

Trendie는 다음과 같은 기능을 제공합니다:

📈 **주간 여행 트렌드 대시보드**: TikTok/YouTube 기반 인기·급상승 여행 해시태그 및 인기 여행 영상 제공  
🧾 **피드백 보고서**: 업로드 영상(또는 자막 텍스트) 분석 기반으로 트렌드 반영 **제목·해시태그·유사 인기 영상** 추천 제공 <br>
🔎 **키워드 기반 연관 영상 검색**: 기획 단계에서 참고할 수 있는 연관 여행 영상 탐색 지원  
⭐ **북마크**: 추천/검색 결과 영상을 저장하고 마이페이지에서 재확인 및 원본 링크 이동   

Trendie Backend는 이러한 기능을 구현하기 위해 다음 역할을 수행합니다:

- YouTube 트렌드 데이터 수집 및 DB 저장(주간 배치 스케줄러 포함)  
- 사용자 입력(영상 파일/자막 텍스트) 처리 및 **Whisper(STT)** 연동을 통한 텍스트 추출 지원  
- 키워드 추출 및 **OpenAI Embedding** 기반 텍스트 임베딩 생성, 유사도 검색/추천을 위한 벡터 처리  
- PostgreSQL + pgvector 기반 데이터 저장 및 검색/추천 결과 제공  
- 사용자 인증 및 보안 처리(JWT, Kakao/Google OAuth)  

---

## ✅ 주요 기능

### 1) 트렌드 대시보드
틱톡과 유튜브 데이터를 수집/분석하여 주간 단위로 다음 정보를 제공합니다.
- 주간 인기/급상승 여행 해시태그
- 인기 여행 동영상 정보(참고용)

### 2) 피드백 보고서
사용자 콘텐츠의 텍스트를 기반으로 키워드를 추출하고, 트렌드를 반영한 추천 결과를 제공합니다.

- 사용자가 말하는 영상: **Whisper 기반 STT**로 음성을 텍스트로 변환
- 무음/자막 기반 영상: 사용자가 자막 텍스트를 직접 입력

제공 결과:
- 맞춤형 제목 추천
- 맞춤형 해시태그 추천
- 연관성이 높은 유사 인기 여행 영상 추천

### 3) 키워드 검색
영상 기획 단계에서 참고할 수 있도록, 키워드로 연관 유튜브 여행 영상을 검색할 수 있습니다.

### 4) 북마크
대시보드/추천/검색에서 제공된 유튜브 영상을 저장하고, 마이페이지에서 다시 확인하거나 원본 링크로 이동할 수 있습니다.

---

## 🎯 기대 효과
- 데이터 기반 콘텐츠 역량 강화
- 기획 효율성과 아이디어 확장 강화
- 채널 성장 기회 확대

---

## 🛠️ 기술 스택

- API 서버: FastAPI, Uvicorn/Gunicorn  
- DB/ORM: PostgreSQL, SQLAlchemy, Alembic  
- Vector: pgvector  
- Cache: Redis  
- Scheduler: APScheduler  
- 외부 API/AI: OpenAI API(**Embedding**, **Whisper**), YouTube Data API v3  
- 인증: JWT, Kakao OAuth, Google OAuth
- Infra & DevOps: AWS EC2, Docker, Docker Compose, GitHub Actions

---

## 📦 사전 설치/필요 항목

- Docker / Docker Compose (권장)
- OpenAI API Key
- YouTube Data API Key

> STT/오디오 처리 기능을 사용하는 경우 환경에 따라 ffmpeg 설치가 필요할 수 있습니다.

---
## 💻 로컬 설치 & 빌드 방법

Docker 없이 로컬에서 실행하려면:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 로컬 실행 시 DATABASE_URL의 host를 환경에 맞게 설정

alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
---

## 🚀 설치 & 빌드 방법 (Docker Compose)

### 0) 📥 레포지토리 클론

```bash
git clone https://github.com/Ewha-SkyEwha/SkyEwha_Backend.git
cd SkyEwha_Backend
```

> 레포 폴더명이 다르면 `cd`만 실제 이름으로 바꿔주세요.

### 1) 환경 변수 설정

프로젝트 루트에 `.env`를 생성하세요.

```bash
cp .env.example .env
# .env 값 채운 뒤 실행
```

### 2) 실행

```bash
docker compose up -d --build
```

### 3) 마이그레이션
DB 스키마가 필요한 경우(최초 실행/스키마 변경 시) 마이그레이션을 수행하세요.
```bash
# fastapi 컨테이너 안에서 Alembic 실행 (서비스명이 fastapi일 때)
docker compose exec fastapi alembic upgrade head
```
> docker-compose.yml에서 FastAPI 서비스명이 다르면 fastapi 부분만 바꿔주세요.

### 4) 종료

```bash
docker compose down
```

---
## 🧪 테스트 방법

> 사전 조건: 위 **실행 방법**의 ~2)까지 완료(컨테이너 실행 상태)

### 1) 컨테이너 상태 확인
```bash
docker compose ps
```

### 2) API 동작 확인

```bash
curl -i http://localhost:8000/ping
```

### 3) 종료

```bash
docker compose down
```
---

## 🐳 Docker Compose 구성

* `trendie`: PostgreSQL + pgvector (`ankane/pgvector`)
* `redis`: Redis 7
* `fastapi`: FastAPI 서버
* `scheduler`: YouTube 수집 배치 컨테이너 (`python app/scheduler/youtube_scheduler.py`)

---

## 🚢 CI/CD 파이프라인

GitHub Actions와 Docker를 활용하여 **자동화된 배포 환경**을 구축했습니다.
`main` 브랜치에 코드가 푸시되면 자동으로 빌드 및 배포가 진행됩니다.

### ♻️ 배포 프로세스 (GitHub Actions)
1.  **Build & Push (CI)**
    * Docker Image 빌드 및 Docker Hub 푸시
    * **Build Cache 적용**: GitHub Actions Cache(`type=gha, mode=max`)를 도입하여 PyTorch, Whisper 등 고용량 AI 라이브러리의 빌드 시간을 획기적으로 단축
2.  **Deploy (CD)**
    * AWS EC2에 SSH 접속 (`appleboy/ssh-action`)
    * `docker-compose`를 통해 최신 이미지 Pull 및 컨테이너 재실행 (환경변수 보안 주입)
---

## 📄 API 문서

* 로컬 Swagger: http://localhost:8000/docs
* 서버 Swagger: https://skyewha-trendie.kr/docs#/

---
## 🔗 링크

* Frontend Repo: https://github.com/Ewha-SkyEwha/SkyEwha_Front
* 틱톡 Creative Center 크롤러: https://github.com/Ewha-SkyEwha/SkyEwha_Tiktok_Crawling

---

## 🗃️ 데이터베이스

pgvector 사용 시 환경에 따라 확장 활성화가 필요할 수 있습니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---
## 📚 사용한 오픈소스 / 외부 서비스
- FastAPI
- SQLAlchemy / Alembic
- PostgreSQL, pgvector
- Redis
- APScheduler
- Docker / Docker Compose
- OpenAI API (Embedding, Whisper)
- YouTube Data API v3
---


