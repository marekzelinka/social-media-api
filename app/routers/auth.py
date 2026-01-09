from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status
from sqlmodel import select

from app.config.security import hash_password
from app.deps import SessionDep
from app.models import User, UserCreate, UserPublic

router = APIRouter(tags=["auth"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic
)
async def register_user(*, session: SessionDep, user: Annotated[UserCreate, Body()]):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = hash_password(user.password)
    user_data = user.model_dump()
    user_data["hashed_password"] = hashed_password
    new_user = User.model_validate(user_data)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
