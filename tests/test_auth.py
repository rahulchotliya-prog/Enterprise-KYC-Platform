import pytest
from uuid import uuid4
from src.auth.models import User
from src.auth.utils import hash_password
from src.database.session import AsyncSessionLocal


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_register_login_flow(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["is_active"] is True

    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_register_duplicate_email_returns_400(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    payload = {"email": email, "password": password, "full_name": "Test User"}

    response_one = await client.post("/auth/register", json=payload)
    assert response_one.status_code == 201

    response_two = await client.post("/auth/register", json=payload)
    assert response_two.status_code == 400
    assert "already exists" in response_two.json()["error"]


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_login_invalid_credentials(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )

    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPassword"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "Invalid credentials"


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_me_endpoint_requires_authorization(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_admin_dashboard_access_denied_for_non_admin(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )

    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    admin_response = await client.get(
        "/auth/admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert admin_response.status_code == 403
    assert admin_response.json()["detail"] == "You are not an admin"


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_admin_dashboard_allows_admin_user(client):
    email = f"admin-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name="Admin User",
            is_admin=True,
        )
        session.add(user)
        await session.commit()

    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    admin_response = await client.get(
        "/auth/admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert admin_response.status_code == 200
    assert admin_response.json()["message"] == "Welcome Admin"
