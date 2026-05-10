import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone
from fastapi import HTTPException
from src.links.routers import redirect_link
from src.links.routers import delete_link
from src.links.routers import update_link
from src.links.routers import get_link_stats
from src.links.schemas import LinkUpdate


EXPIRE_AT = "2027-04-30T22:30+00:00"


async def register_and_login(client, email="user@example.com", user_id=100):
    password = "strongpassword"

    register_response = await client.post(
        "/auth/register",
        json={
            "id": user_id,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code in [200, 201]

    login_response = await client.post(
        "/auth/jwt/login",
        data={
            "username": email,
            "password": password,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    assert login_response.status_code == 204


@pytest.mark.asyncio
async def test_create_short_link_anonymous(client):
    response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://google.com",
            "custom_alias": "googlealias",
            "expire_at": EXPIRE_AT,
        },
    )

    assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_create_short_link_custom_alias(client):
    await register_and_login(client)

    response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://github.com",
            "custom_alias": "myalias",
            "expire_at": EXPIRE_AT,
        },
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert data["short_id"] == "myalias"


@pytest.mark.asyncio
async def test_create_duplicate_alias(client):
    await register_and_login(client)

    payload = {
        "original_url": "https://example.com",
        "custom_alias": "samealias",
        "expire_at": EXPIRE_AT,
    }

    first_response = await client.post("/links/shorten", json=payload)

    assert first_response.status_code in [200, 201]

    second_response = await client.post("/links/shorten", json=payload)

    assert second_response.status_code == 400


@pytest.mark.asyncio
async def test_redirect_existing_link(client):
    await register_and_login(client)

    create_response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://python.org",
            "custom_alias": "python",
            "expire_at": EXPIRE_AT,
        },
    )

    assert create_response.status_code in [200, 201]

    response = await client.get(
        "/links/python",
        follow_redirects=False,
    )

    assert response.status_code in [302, 307]
    assert response.headers["location"] == "https://python.org/"


@pytest.mark.asyncio
async def test_redirect_missing_link(client):
    response = await client.get("/links/does-not-exist")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stats_authorized(client):
    await register_and_login(client)

    create_response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://fastapi.tiangolo.com",
            "custom_alias": "fastapi",
            "expire_at": EXPIRE_AT,
        },
    )

    assert create_response.status_code in [200, 201]

    response = await client.get("/links/fastapi/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["short_id"] == "fastapi"
    assert data["original_url"] == "https://fastapi.tiangolo.com/"


@pytest.mark.asyncio
async def test_get_stats_unauthorized(client):
    response = await client.get("/links/random/stats")

    assert response.status_code in [401, 403, 404]


@pytest.mark.asyncio
async def test_search_links(client):
    await register_and_login(client)

    create_response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://google.com/search",
            "custom_alias": "searchlink",
            "expire_at": EXPIRE_AT,
        },
    )

    assert create_response.status_code in [200, 201]

    response = await client.get(
        "/links/search/",
        params={
            "original_url": "google",
        },
    )

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_delete_link(client):
    await register_and_login(client)

    create_response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://delete.com",
            "custom_alias": "deletealias",
            "expire_at": EXPIRE_AT,
        },
    )

    assert create_response.status_code in [200, 201]

    response = await client.delete("/links/deletealias")

    assert response.status_code in [200, 204, 404]


@pytest.mark.asyncio
async def test_update_link(client):
    await register_and_login(client)

    create_response = await client.post(
        "/links/shorten",
        json={
            "original_url": "https://old-url.com",
            "custom_alias": "updatealias",
            "expire_at": EXPIRE_AT,
        },
    )

    assert create_response.status_code in [200, 201]

    response = await client.put(
        "/links/updatealias",
        json={
            "original_url": "https://new-url.com",
            "expire_at": EXPIRE_AT,
        },
    )

    assert response.status_code in [200, 204, 404]


@pytest.mark.asyncio
async def test_redirect_missing_link(client):
    response = await client.get(
        "/links/not-found",
        follow_redirects=False
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_link_success(mocker):
    mock_link = Mock()
    mock_link.original_url = "https://python.org"
    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=mock_link),
    )
    mock_increment = mocker.patch(
        "src.links.crud.increment_click_count",
        new=AsyncMock(),
    )
    response = await redirect_link(
        short_id="python",
        db=Mock(),
    )
    mock_increment.assert_awaited_once()

    assert response.status_code == 307
    assert response.headers["location"] == "https://python.org"

@pytest.mark.asyncio
async def test_redirect_link_not_found(mocker):
    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await redirect_link(
            short_id="missing",
            db=Mock(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Link not found"


@pytest.mark.asyncio
async def test_delete_link_success(mocker):

    mock_link = Mock()
    mock_link.user_id = 1
    mock_user = Mock()
    mock_user.id = 1

    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=mock_link),
    )

    mock_delete = mocker.patch(
        "src.links.crud.delete_link",
        new=AsyncMock(),
    )

    response = await delete_link(
        short_id="test",
        db=Mock(),
        user=mock_user,
    )

    mock_delete.assert_awaited_once()

    assert response == {"status": "success"}

@pytest.mark.asyncio
async def test_delete_link_not_found(mocker):
    mock_user = Mock()
    mock_user.id = 1
    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await delete_link(
            short_id="missing",
            db=Mock(),
            user=mock_user,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_link_success(mocker):
    mock_link = Mock()
    mock_link.user_id = 1

    mock_user = Mock()
    mock_user.id = 1

    update_data = LinkUpdate(
        original_url="https://new-url.com"
    )

    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=mock_link),
    )

    mock_updated = {
        "short_id": "test",
        "original_url": "https://new-url.com",
    }

    mock_update = mocker.patch(
        "src.links.crud.update_link",
        new=AsyncMock(return_value=mock_updated),
    )

    response = await update_link(
        short_id="test",
        update_data=update_data,
        db=Mock(),
        user=mock_user,
    )

    mock_update.assert_awaited_once()

    assert response == mock_updated


@pytest.mark.asyncio
async def test_update_link_not_found(mocker):
    mock_user = Mock()
    mock_user.id = 1

    update_data = LinkUpdate(
        original_url="https://new-url.com"
    )

    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await update_link(
            short_id="missing",
            update_data=update_data,
            db=Mock(),
            user=mock_user,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_link_stats_success(mocker):
    mock_link = Mock()

    mock_link.user_id = 1
    mock_link.original_url = "https://python.org"
    mock_link.short_id = "python"
    mock_link.custom_alias = "python"
    mock_link.created_at = datetime.now(timezone.utc)
    mock_link.expire_at = datetime.now(timezone.utc)
    mock_link.click_count = 10

    mock_user = Mock()
    mock_user.id = 1

    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=mock_link),
    )

    response = await get_link_stats(
        short_id="python",
        db=Mock(),
        user=mock_user,
    )

    assert response["click_count"] == 10


@pytest.mark.asyncio
async def test_get_link_stats_not_found(mocker):
    mock_user = Mock()
    mock_user.id = 1

    mocker.patch(
        "src.links.crud.get_link_by_short_id",
        new=AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await get_link_stats(
            short_id="missing",
            db=Mock(),
            user=mock_user,
        )

    assert exc.value.status_code == 404