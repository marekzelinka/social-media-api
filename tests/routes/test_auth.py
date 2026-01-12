import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.models import User, UserCreate


@pytest.fixture
def user(session: Session) -> UserCreate:
    user = UserCreate.model_validate(
        {
            "username": "hello123",
            "email": "hello123@gmail.com",
            "password": "password123",
        }
    )
    hashed_password = hash_password(user.password)
    user_dict = user.model_dump()
    new_user = User.model_validate(
        user_dict, update={"hashed_password": hashed_password}
    )
    session.add(new_user)
    session.commit()
    return user


def test_register(client: TestClient) -> None:
    r = client.post(
        "/register",
        json={
            "username": "hello123",
            "email": "hello123@gmail.com",
            "password": "password123",
        },
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["email"] == "hello123@gmail.com"


def test_token(client: TestClient, user: UserCreate) -> None:
    r = client.post(
        "/token",
        data={
            "username": user.username,
            "password": user.password,
        },
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["access_token"]
