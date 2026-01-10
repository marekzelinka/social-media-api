from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import config
from app.deps import SessionDep
from app.routers import auth, posts, votes

app = FastAPI(title="Social Media API", version="1.0.0")

# Set all CORS enabled origins
if config.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=config.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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
