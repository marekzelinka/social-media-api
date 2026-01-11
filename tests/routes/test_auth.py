from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models import UserPublic

client = TestClient(app)


def test_register() -> None:
    r = client.post(
        "/register",
        json={
            "username": "hello145",
            "email": "hello145@gmail.com",
            "password": "password145",
        },
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    new_user = UserPublic(**data)
    assert new_user.email == "hello145@gmail.com"
