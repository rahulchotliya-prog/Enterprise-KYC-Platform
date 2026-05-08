import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.auth.dependencies import get_current_user

from uuid import uuid4

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
async def override_auth():
    app.dependency_overrides[get_current_user] = fake_user
    yield
    app.dependency_overrides.clear()