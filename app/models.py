import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    hashed_password: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    posts: list[Post] = Relationship(back_populates="owner", cascade_delete=True)


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str


class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str
    published: bool = Field(default=True)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    owner: User = Relationship(back_populates="posts")


class PostCreate(PostBase):
    pass


class PostPublic(PostBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime

    owner_id: uuid.UUID


class PostUpdate(SQLModel):
    published: bool | None = None
