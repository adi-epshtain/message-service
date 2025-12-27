"""Pytest configuration and fixtures."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app


# Create file-based SQLite database for tests (more reliable than :memory:)
TEST_DB_PATH = "./test_messages.db"
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh async database session for each test."""
    # Drop all tables first to ensure clean state
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            # Clean up tables (but keep the file to avoid Windows file locking issues)
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession):
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

