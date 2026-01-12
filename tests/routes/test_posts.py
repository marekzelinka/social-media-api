from collections.abc import Sequence

from fastapi.testclient import TestClient

from app.models import Post, PostPublicWithVotes


def test_read_posts(
    client: TestClient, db_posts: Sequence[Post], token_headers: dict[str, str]
):
    r = client.get("/posts/", headers=token_headers)
    assert r.status_code == 200
    data = r.json()
    posts = [PostPublicWithVotes.model_validate(post) for post in data]
    assert len(posts) == len(db_posts)
    assert str(posts[0].Post.id) == str(db_posts[0].id)
