import pytest

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from user_service.main import app
from common.core.database import get_db
from common.tests.db_conf import create_test_engine, setup_test_db, teardown_test_db, create_db_session, close_db_session

pytest_plugins = ["anyio"]

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# Setup test database engine
@pytest.fixture(scope="session")
def test_engine():
    engine = create_test_engine()
    return engine


# Setup test database
@pytest.fixture(scope="session")
async def setup_db(test_engine: AsyncEngine):
    await setup_test_db(test_engine)
    yield
    await teardown_test_db(test_engine)


# Setup test database session
@pytest.fixture
async def db_session(test_engine: AsyncEngine, setup_db):
    conn, transaction, session = await create_db_session(test_engine)
    try:
        yield session
    finally:
        await close_db_session(session, transaction, conn)


# Setup http client
@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://users_test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
