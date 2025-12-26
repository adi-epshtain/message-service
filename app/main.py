from fastapi import FastAPI

from app.api.messages import router as messages_router
from app.db.base import Base
from app.db.session import engine
from app.models import Message  # noqa: F401 - Import to register models

app = FastAPI(
    title="Message Service API",
    description="A production-grade chat messages API",
    version="0.1.0",
)


@app.on_event("startup")
def create_tables() -> None:
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


app.include_router(messages_router)


