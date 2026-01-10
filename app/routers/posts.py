import uuid
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlmodel import col, func, select

from app.deps import CurrentUserDep, SessionDep
from app.models import (
    Post,
    PostCreate,
    PostPublic,
    PostPublicWithVotes,
    PostUpdate,
    Vote,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostPublic)
async def create_post(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    post: Annotated[PostCreate, Body()],
):
    db_post = Post.model_validate(post, update={"owner_id": current_user.id})
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.get("/", response_model=list[PostPublicWithVotes])
async def read_posts(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    published: Annotated[bool | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
):
    query = (
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .where(Post.owner_id == current_user.id)
        .group_by(Post.id)
    )
    if published:
        query = query.where(Post.published == published)
    if search:
        query = query.where(col(Post.title).icontains(search))
    results = session.exec(query.offset(offset).limit(limit)).all()
    return results


@router.get("/{post_id}", response_model=PostPublic)
async def read_post(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    post_id: Annotated[uuid.UUID, Path()],
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough premissions"
        )
    return post


@router.put("/{post_id}", response_model=PostPublic)
async def update_post(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    post_id: Annotated[uuid.UUID, Path()],
    post: Annotated[PostUpdate, Body()],
):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if db_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough premissions"
        )
    update_dict = post.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(update_dict)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    post_id: Annotated[uuid.UUID, Path()],
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough premissions"
        )
    session.delete(post)
    session.commit()
