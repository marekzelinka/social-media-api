from sqlmodel import SQLModel, create_engine

from app.core.config import get_config

DATABASE_URL = str(get_config().database_url)
engine = create_engine(DATABASE_URL)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
