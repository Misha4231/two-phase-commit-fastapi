import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy import NullPool
from sqlalchemy.engine import URL

from common.models.base import Model


def create_test_engine() -> AsyncEngine:
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
    )
    return create_async_engine(DATABASE_URL, poolclass=NullPool)


async def setup_test_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def teardown_test_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
    await engine.dispose()


async def create_db_session(engine: AsyncEngine):
    conn = await engine.connect()
    transaction = await conn.begin()
    session_factory = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint", # data is not really saved in database so that tests are isolated
    )
    return conn, transaction, session_factory()


async def close_db_session(session: AsyncSession, transaction, conn):
    await session.close()
    await transaction.rollback()
    await conn.close()
