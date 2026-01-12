from collections.abc import Sequence

from fastapi import status
from fastapi.testclient import TestClient

from app.models import Post, PostPublicWithVotes


def test_read_posts(
    client: TestClient,
    db_posts: Sequence[Post],
) -> None:
    r = client.get("/posts/")
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    posts = sorted(
        [PostPublicWithVotes.model_validate(post) for post in data],
        key=lambda result: result.Post.id,
    )
    db_posts = sorted(db_posts, key=lambda post: post.id)
    assert len(posts) == len(db_posts)
    assert posts[0].Post.id == db_posts[0].id


def test_read_post(client: TestClient, db_posts: Sequence[Post]) -> None:
    r = client.get(f"/posts/{db_posts[0].id}")
    assert r.status_code == status.HTTP_200_OK
