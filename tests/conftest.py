import os

# ENV VARIABLES
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASS"] = "postgres"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "shortist_test"
os.environ["SECRET"] = "TEST_SECRET"


import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from src.main import app
from src.database import Base, get_db


# TEST DATABASE
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False
)


TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    expire_on_commit=False
)


# OVERRIDE DATABASE
async def override_get_db():

    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# CREATE/DROP TABLES
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine_test.dispose()


# CLEAR DATABASE BEFORE EACH TEST
@pytest_asyncio.fixture(autouse=True)
async def clear_tables():

    async with TestingSessionLocal() as session:

        await session.execute(text("DELETE FROM links"))
        await session.execute(text("DELETE FROM user"))

        await session.commit()

    yield


# TEST CLIENT
@pytest_asyncio.fixture
async def client():

    async with AsyncClient(
        transport=ASGITransport(
            app=app,
            raise_app_exceptions=True
        ),
        base_url="https://test"
    ) as ac:

        yield ac