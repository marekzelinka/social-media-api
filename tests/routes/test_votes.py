from collections.abc import Sequence

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Headers

from app.models import Post


def test_add_vote(
    client: TestClient, db_posts: Sequence[Post], token_headers: Headers
) -> None:
    r = client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": str(db_posts[0].id), "dir": 1},
    )
    assert r.status_code == status.HTTP_200_OK


def test_add_vote_twice(
    client: TestClient, db_posts: Sequence[Post], token_headers: Headers
) -> None:
    client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": str(db_posts[0].id), "dir": 1},
    )
    r = client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": str(db_posts[0].id), "dir": 1},
    )
    assert r.status_code == status.HTTP_409_CONFLICT


def test_add_vote_with_nonexisting_post(
    client: TestClient, token_headers: Headers
) -> None:
    nonexisting_valid_id = "63df3284-94fe-42e2-be37-dfc6d38f374e"
    r = client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": nonexisting_valid_id, "dir": 1},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_vote(
    client: TestClient, db_posts: Sequence[Post], token_headers: Headers
) -> None:
    # Start by adding a vote and then delete it
    client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": str(db_posts[0].id), "dir": 1},
    )
    r = client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": str(db_posts[0].id), "dir": 0},
    )
    assert r.status_code == status.HTTP_200_OK


def test_delete_vote_with_no_votes_post(
    client: TestClient, db_posts: Sequence[Post], token_headers: Headers
) -> None:
    r = client.post(
        "/votes/",
        headers=token_headers,
        json={"post_id": str(db_posts[0].id), "dir": 0},
    )
    assert r.status_code == status.HTTP_409_CONFLICT


def test_vote_unauthorized_without_headers(
    client: TestClient,
    db_posts: Sequence[Post],
) -> None:
    r = client.post("/votes/", json={"post_id": str(db_posts[0].id), "dir": 1})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
