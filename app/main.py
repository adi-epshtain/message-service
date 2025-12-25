from fastapi import FastAPI

from app.api.messages import router as messages_router

app = FastAPI(
    title="Message Service API",
    description="A production-grade chat messages API",
    version="0.1.0",
)

app.include_router(messages_router)


