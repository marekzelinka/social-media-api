from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.core.db import create_db_and_tables
from app.deps import SessionDep
from app.routers import auth, posts, votes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Social Media API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(votes.router)


@app.get(
    "/health",
    tags=["status"],
    summary="Perform a Health Check",
    status_code=status.HTTP_200_OK,
)
async def read_health(*, session: SessionDep):
    return {"status": "ok"}
