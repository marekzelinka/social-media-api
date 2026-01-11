from collections.abc import Generator

import pytest
from alembic.config import Config, command
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.core.config import config
from app.deps import get_session
from app.main import app


# Setup a single engine for the entire test session
@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(str(config.test_database_url))


# Runs db migrations once per test session
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(config.test_database_url))
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


@pytest.fixture(name="session")
def session_fixture(engine: Engine) -> Generator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
