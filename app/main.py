from fastapi import FastAPI, status

from app.deps import SessionDep
from app.routers import auth, posts, votes

app = FastAPI(title="Social Media API", version="1.0.0")

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
