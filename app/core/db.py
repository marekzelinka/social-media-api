from sqlmodel import create_engine

from app.core.config import config

engine = create_engine(str(config.database_url))
