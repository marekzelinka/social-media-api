import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.models import User, UserPublic


@pytest.fixture
def form_data(session: Session) -> dict[str, str]:
    user_dict = {
        "username": "hello123",
        "email": "hello123@gmail.com",
        "password": "password123",
    }
    hashed_password = hash_password(user_dict["password"])
    new_user = User.model_validate(
        user_dict, update={"hashed_password": hashed_password}
    )
    session.add(new_user)
    session.commit()
    return {"username": new_user.username, "password": user_dict["password"]}


def test_register(client: TestClient) -> None:
    response = client.post(
        "/register",
        json={
            "username": "hello123",
            "email": "hello123@gmail.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    new_user = UserPublic(**data)
    assert new_user.email == "hello123@gmail.com"


def test_token(client: TestClient, form_data) -> None:
    response = client.post(
        "/token",
        data=form_data,
    )
    assert response.status_code == status.HTTP_200_OK
