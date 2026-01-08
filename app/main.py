from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.config.db import create_db_and_tables
from app.deps import SessionDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Social Media API", lifespan=lifespan)


@app.get(
    "/health",
    tags=["status"],
    summary="Perform a Health Check",
    status_code=status.HTTP_200_OK,
)
async def read_health(*, session: SessionDep):
    return {"status": "ok"}
