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


@pytest.mark.parametrize(
    "username, password, status_code",
    [
        # Wrong email with a valid password should return 403
        ("wrongemail", "password123", status.HTTP_401_UNAUTHORIZED),
        # Valid email with wrong password should return 403
        ("hello123", "wrong_password", status.HTTP_401_UNAUTHORIZED),
        # Both email and password are incorrect; should return 403
        ("wrongemail", "wrong_password", status.HTTP_401_UNAUTHORIZED),
        # Missing email should fail schema validatiion and return 422
        (None, "wrong_password", status.HTTP_422_UNPROCESSABLE_CONTENT),
        # Missing password should fail schema validatiion and return 422
        ("hello123", None, status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
)
def test_incorrect_token(
    client: TestClient, username: str, password: str, status_code: int
) -> None:
    r = client.post(
        "/token",
        data={
            "username": username,
            "password": password,
        },
    )
    assert r.status_code == status_code
    if status_code == status.HTTP_401_UNAUTHORIZED:
        data = r.json()
        assert "access_token" not in data
