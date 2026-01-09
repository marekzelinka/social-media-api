from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, status

from app.deps import SessionDep
from app.models import PostModel
from app.schema import Post

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(*, session: SessionDep, post: Annotated[PostModel, Body()]):
    new_post = Post(**post.model_dump())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


@router.get("/")
async def read_posts(*, session: SessionDep):
    posts = session.query(Post).all()
    return posts


@router.get("/{post_id}")
async def read_post(*, session: SessionDep, post_id: Annotated[int, Path()]):
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.put("/{post_id}")
async def update_post(
    *,
    session: SessionDep,
    post_id: Annotated[int, Path()],
    post: Annotated[PostModel, Body()],
):
    post_query = session.query(Post).filter(Post.id == post_id)
    db_post = post_query.first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    session.commit()
    updated_post = post_query.first()
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(*, session: SessionDep, post_id: Annotated[int, Path()]):
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    session.delete(post)
    session.commit()
