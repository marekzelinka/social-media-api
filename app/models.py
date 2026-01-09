from pydantic import BaseModel


class PostModel(BaseModel):
    title: str
    content: str
    published: bool | None = True
