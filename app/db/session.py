"""Database session management."""

import os
from pathlib import Path
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.db.base import Base

# Get database URL from environment or construct from path
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    # Fallback to path-based configuration
    DB_PATH = os.getenv("DATABASE_PATH", "./messages.db")
    # Ensure parent directory exists
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
else:
    # Convert sync URL to async if needed
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
