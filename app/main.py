from fastapi import FastAPI

app = FastAPI(
    title="Message Service API",
    description="A production-grade chat messages API",
    version="0.1.0",
)


@app.post("/messages")
async def create_message() -> dict:
    """Create a new message."""
    return {}


@app.get("/rooms/{room_id}/messages")
async def get_room_messages(room_id: int) -> dict:
    """Get messages for a specific room with pagination."""
    return {}

