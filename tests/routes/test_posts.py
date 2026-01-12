from collections.abc import Sequence

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, hash_password
from app.models import Post, PostPublic, PostPublicWithVotes, User
from tests.conftest import _TestDBUser


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


def test_read_post_with_nonexisting_id(client: TestClient) -> None:
    nonexisting_id = "63df3284-94fe-42e2-be37-dfc6d38f374e"
    r = client.get(f"/posts/{nonexisting_id}")
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_read_post_with_invalid_id(client: TestClient) -> None:
    invalid_id = "invalid_post_id"
    r = client.get(f"/posts/{invalid_id}")
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("awesome new title", "amesome new content", True),
        ("favorite pizza", "i love pepperoni", False),
        ("tallest skyscrapers", "wahoo", True),
    ],
)
def test_create_post_with_valid_data(
    client: TestClient,
    db_user: _TestDBUser,
    token_headers: dict[str, str],
    title: str,
    content: str,
    published: bool,
) -> None:
    r = client.post(
        "/posts/",
        headers=token_headers,
        json={"title": title, "content": content, "published": published},
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    new_post = PostPublic.model_validate(data)
    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == published
    assert new_post.owner_id == db_user.id


def test_create_post_default_published_true(
    client: TestClient,
    db_user: _TestDBUser,
    token_headers: dict[str, str],
) -> None:
    r = client.post(
        "/posts",
        headers=token_headers,
        json={"title": "arbitrary title", "content": "content"},
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    new_post = PostPublic.model_validate(data)
    assert new_post.title == "arbitrary title"
    assert new_post.content == "content"
    assert new_post.published is True
    assert new_post.owner_id == db_user.id


def test_create_post_unauthorized_without_headers(client: TestClient) -> None:
    r = client.post("/posts/")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post(
    client: TestClient,
    db_posts: Sequence[Post],
    token_headers: dict[str, str],
) -> None:
    r = client.delete(f"/posts/{db_posts[0].id}", headers=token_headers)
    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_delete_post_unauthorized(client: TestClient, db_posts: Sequence[Post]) -> None:
    r = client.delete(f"/posts/{db_posts[0].id}")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post_with_nonexisting_id(
    client: TestClient,
    token_headers: dict[str, str],
) -> None:
    nonexisting_id = "63df3284-94fe-42e2-be37-dfc6d38f374e"
    r = client.delete(f"/posts/{nonexisting_id}", headers=token_headers)
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_post_with_different_owner(
    session: Session,
    client: TestClient,
    db_posts: Sequence[Post],
) -> None:
    new_user = User(
        username="123hello",
        email="123hello@gmail.com",
        hashed_password=hash_password("123hello"),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    new_user_access_token = create_access_token(data={"sub": "123hello"})
    new_user_token_headers = {"Authorization": f"Bearer {new_user_access_token}"}
    r = client.delete(f"/posts/{db_posts[0].id}", headers=new_user_token_headers)
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_update_post(
    client: TestClient, db_posts: Sequence[Post], token_headers: dict[str, str]
) -> None:
    r = client.put(
        f"/posts/{db_posts[0].id}", headers=token_headers, json={"published": False}
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["published"] is False


def test_update_post_with_invalid_data(
    client: TestClient, db_posts: Sequence[Post], token_headers: dict[str, str]
) -> None:
    r = client.put(f"/posts/{db_posts[0].id}", headers=token_headers)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_post_unauthorized(client: TestClient, db_posts: Sequence[Post]) -> None:
    r = client.put(f"/posts/{db_posts[0].id}", json={"published": False})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_post_with_nonexisting_id(
    client: TestClient,
    token_headers: dict[str, str],
) -> None:
    nonexisting_id = "63df3284-94fe-42e2-be37-dfc6d38f374e"
    r = client.put(
        f"/posts/{nonexisting_id}", headers=token_headers, json={"published": False}
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_with_different_owner(
    session: Session,
    client: TestClient,
    db_posts: Sequence[Post],
) -> None:
    new_user = User(
        username="123hello",
        email="123hello@gmail.com",
        hashed_password=hash_password("123hello"),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    new_user_access_token = create_access_token(data={"sub": "123hello"})
    new_user_token_headers = {"Authorization": f"Bearer {new_user_access_token}"}
    r = client.put(
        f"/posts/{db_posts[0].id}",
        headers=new_user_token_headers,
        json={"published": False},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN
