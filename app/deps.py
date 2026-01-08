from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.db import SessionLocal


def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_db_session)]
