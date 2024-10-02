import pytest
from httpx import AsyncClient

USER_1_PARAMS = {
    "api_key": "test",
    "username": "test_username",
    "name": "test_name",
    "surname": "test_surname",
}
USER_2_PARAMS = {
    "api_key": "test_2",
    "username": "test_username_2",
    "name": "test_name_2",
    "surname": "test_surname_2",
}
USER_3_PARAMS = {
    "api_key": "test_3",
    "username": "test_username_3",
    "name": "test_name_3",
    "surname": "test_surname_3",
}


@pytest.mark.parametrize(
    ["body", "id"], [(USER_1_PARAMS, 1), (USER_2_PARAMS, 2), (USER_3_PARAMS, 3)]
)
async def test_add_user(body: dict, id: int, ac: AsyncClient):
    response = await ac.post(url="/users", json=body)

    body.update({"id": id})
    assert response.status_code == 201
    assert response.json() == body


async def test_get_user_profile_me(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.get(url="/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "result": True,
        "user": {"id": 1, "name": "test_username", "followers": [], "following": []},
    }


async def test_get_user_profile_id(ac: AsyncClient):
    response = await ac.get(url="/users/2")

    assert response.status_code == 200
    assert response.json() == {
        "result": True,
        "user": {"id": 2, "name": "test_username_2", "followers": [], "following": []},
    }


async def test_add_media(ac: AsyncClient):
    with open("tests/test_image.jpg", "rb") as media_file:
        image = media_file.read()
        response = await ac.post(
            url="/medias", files={"file": ("test_image.jpg", image, "image/jpeg")}
        )

        assert response.status_code == 201
        assert response.json() == {"result": True, "media_id": 1}


@pytest.mark.parametrize(["api_key", "id"], [("test", 1), ("test_2", 2), ("test_3", 3)])
async def test_add_tweet(ac: AsyncClient, api_key: str, id: int):
    headers = {"api-key": api_key}
    body = {"tweet_data": "test_text", "tweet_media_ids": []}
    if id == 1:
        body["tweet_media_ids"].append(1)
    response = await ac.post(url="/tweets", headers=headers, json=body)

    assert response.status_code == 201
    assert response.json() == {"result": True, "tweet_id": id}


async def test_add_like_to_tweet(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.post(url="/tweets/2/likes", headers=headers)

    assert response.status_code == 201
    assert response.json() == {"result": True}


async def test_add_following(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.post(url="/users/3/follow", headers=headers)

    assert response.status_code == 201
    assert response.json() == {"result": True}


async def test_get_tweets(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.get(url="tweets", headers=headers)

    result = {
        "result": True,
        "tweets": [
            {
                "attachments": [],
                "author": {"id": 3, "name": "test_username_3"},
                "content": "test_text",
                "id": 3,
                "likes": [],
            },
            {
                "attachments": [],
                "author": {"id": 2, "name": "test_username_2"},
                "content": "test_text",
                "id": 2,
                "likes": [{"name": "test_username", "user_id": 1}],
            },
            {
                "attachments": ["/api/medias/1"],
                "author": {"id": 1, "name": "test_username"},
                "content": "test_text",
                "id": 1,
                "likes": [],
            },
        ],
    }

    assert response.status_code == 200
    assert response.json() == result


async def test_get_media(ac: AsyncClient):
    response = await ac.get(url="/medias/1")

    with open("tests/test_image.jpg", "rb") as media_file:
        image = media_file.read()

        assert response.content == image


async def test_delete_tweet(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.delete(url="/tweets/1", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"result": True}


async def test_delete_following(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.delete(url="/users/3/follow", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"result": True}


async def test_get_tweets_2(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.get(url="/tweets", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "result": True,
        "tweets": [
            {
                "attachments": [],
                "author": {"id": 2, "name": "test_username_2"},
                "content": "test_text",
                "id": 2,
                "likes": [{"name": "test_username", "user_id": 1}],
            },
            {
                "attachments": [],
                "author": {"id": 3, "name": "test_username_3"},
                "content": "test_text",
                "id": 3,
                "likes": [],
            },
        ],
    }


async def test_delete_like(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.delete(url="/tweets/2/likes", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"result": True}


async def test_get_tweets_3(ac: AsyncClient):
    headers = {"api-key": "test"}
    response = await ac.get(url="/tweets", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "result": True,
        "tweets": [
            {
                "attachments": [],
                "author": {"id": 2, "name": "test_username_2"},
                "content": "test_text",
                "id": 2,
                "likes": [],
            },
            {
                "attachments": [],
                "author": {"id": 3, "name": "test_username_3"},
                "content": "test_text",
                "id": 3,
                "likes": [],
            },
        ],
    }
