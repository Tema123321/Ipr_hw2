import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "id": 1,
            "email": "test@example.com",
            "password": "strongpassword"
        }
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_register_duplicate_user(client):
    payload = {
        "id": 2,
        "email": "duplicate@example.com",
        "password": "strongpassword"
    }

    await client.post("/auth/register", json=payload)

    response = await client.post("/auth/register", json=payload)

    assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_login_user(client):
    payload = {
        "id": 3,
        "email": "login@example.com",
        "password": "strongpassword"
    }

    register_response = await client.post(
        "/auth/register",
        json=payload
    )

    assert register_response.status_code in [200, 201]

    response = await client.post(
        "/auth/jwt/login",
        data={
            "username": payload["email"],
            "password": payload["password"]
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/auth/jwt/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert response.status_code in [400, 401]