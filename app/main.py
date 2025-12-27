from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.messages import router as messages_router
from app.db.base import Base
from app.db.session import engine
from app.models import Message  # noqa: F401 - Import to register models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown (if needed in the future)


app = FastAPI(
    title="Message Service API",
    description="A production-grade chat messages API",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(health_router)
app.include_router(messages_router)


