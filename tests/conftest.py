import pytest
import pytest_asyncio
import redis.asyncio as redis
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from uuid import uuid4

from src.config.settings import settings
from src.database.base import Base
from src.main import app
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.auth.utils import hash_password
from src.database.session import AsyncSessionLocal
from src.infrastructure.redis import redis_client


def _get_sync_database_url():
    if settings.DATABASE_URL:
        db_url = settings.DATABASE_URL
    else:
        db_url = getattr(settings, "SYNC_DATABASE_URL", None)

    if not db_url:
        raise RuntimeError(
            "DATABASE_URL or SYNC_DATABASE_URL must be configured for tests."
        )

    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)

    return db_url


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    sync_database_url = _get_sync_database_url()
    engine = create_engine(sync_database_url, poolclass=NullPool)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_database_between_tests():
    sync_database_url = _get_sync_database_url()
    engine = create_engine(sync_database_url, poolclass=NullPool)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture(autouse=True)
async def clear_redis_cache():
    async_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await async_client.delete("analytics_summary")
    finally:
        await async_client.aclose()

    yield

    async_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await async_client.delete("analytics_summary")
    finally:
        await async_client.aclose()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    


def fake_user():
    class FakeUser:
        id = "1c934798-e5a8-4095-b931-62fe12392c31"
        is_admin = True

    return FakeUser()

@pytest_asyncio.fixture(autouse=True)
async def override_auth(request):
    if request.node.get_closest_marker("real_auth"):
        yield
        return

    app.dependency_overrides[get_current_user] = fake_user
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    payload = {"email": email, "password": password, "full_name": "Test User"}

    register_response = await client.post("/auth/register", json=payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


async def create_admin_user(email: str, password: str, full_name: str):
    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_admin=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user