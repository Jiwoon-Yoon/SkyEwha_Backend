# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """
    기본 경로(/ping)로 요청을 보냈을 때 200 응답이 오는지 확인합니다.
    """
    response = client.get("/ping")
    assert response.status_code == 200