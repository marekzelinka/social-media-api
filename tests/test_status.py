from fastapi import status
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["status"] == "ok"
