import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import NullPool
from sqlalchemy.engine import URL

from user_service.main import app
from user_service.core.database import get_db
from user_service.models.base import Model

pytest_plugins = ["anyio"]

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio" 


# Setup test database engine
@pytest.fixture(scope="session")
def test_engine():
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
    )
    engine = create_async_engine(
        DATABASE_URL,
        poolclass=NullPool
    )
    return engine


# Setup test database
@pytest.fixture(scope="session")
async def setup_db(test_engine: AsyncEngine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

    await test_engine.dispose()


# Setup test database session
@pytest.fixture
async def db_session(test_engine: AsyncEngine, setup_db):
    conn = await test_engine.connect()
    transaction = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
            await conn.close()


# Setup http client
@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
