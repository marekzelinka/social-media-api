from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["status"] == "ok"
