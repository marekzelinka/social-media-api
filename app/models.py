import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str | None = Field(default=None)
    published: bool = Field(default=True)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class PostCreate(PostBase):
    pass


class PostPublic(PostBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
