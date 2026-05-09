import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from src.config.settings import settings
from src.database.base import Base
from src.main import app
from src.auth.dependencies import get_current_user


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