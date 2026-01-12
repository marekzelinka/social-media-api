from collections.abc import Generator, Sequence
from typing import Any

import pytest
from alembic.config import Config, command
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select

from app.core.config import config
from app.core.security import create_access_token, hash_password
from app.deps import get_session
from app.main import app
from app.models import Post, User, UserCreate


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(str(config.test_database_url))


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None]:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(config.test_database_url))
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


@pytest.fixture(name="session")
def session_fixture(engine: Engine) -> Generator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    # Set session ovverride before startup lifecycle events trigger
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def db_user(session: Session) -> dict[str, Any]:
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
    session.refresh(new_user)
    return {**user_dict, "id": new_user.id}


@pytest.fixture
def db_posts(session: Session, db_user: dict[str, Any]) -> Sequence[Post]:
    posts_data = [
        {"title": "first title", "content": "first content", "owner_id": db_user["id"]},
        {"title": "2nd title", "content": "2nd content", "owner_id": db_user["id"]},
        {"title": "3rd title", "content": "3rd content", "owner_id": db_user["id"]},
    ]
    posts: Sequence[Post] = [Post.model_validate(post) for post in posts_data]
    session.add_all(posts)
    session.commit()
    posts = session.exec(select(Post)).all()
    return posts


@pytest.fixture
def token_headers(db_user: dict[str, Any]) -> dict[str, str]:
    access_token = create_access_token(data={"sub": db_user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
