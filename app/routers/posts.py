import uuid
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlmodel import select

from app.deps import SessionDep
from app.models import Post, PostCreate, PostPublic, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostPublic, status_code=status.HTTP_201_CREATED)
async def create_post(*, session: SessionDep, post: Annotated[PostCreate, Body()]):
    db_post = Post.model_validate(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.get("/", response_model=list[PostPublic])
async def read_posts(
    *,
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    published: Annotated[bool | None, Query()] = None,
):
    query = select(Post)
    if published:
        query = query.where(Post.published == published)
    posts = session.exec(query.offset(offset).limit(limit)).all()
    return posts


@router.get("/{post_id}", response_model=PostPublic)
async def read_post(*, session: SessionDep, post_id: Annotated[uuid.UUID, Path()]):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.patch("/{post_id}", response_model=PostPublic)
async def update_post(
    *,
    session: SessionDep,
    post_id: Annotated[uuid.UUID, Path()],
    post: Annotated[PostUpdate, Body()],
):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    post_data = post.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(post_data)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(*, session: SessionDep, post_id: Annotated[uuid.UUID, Path()]):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    session.delete(post)
    session.commit()
