"""Message API endpoints."""

from app.core.logging import logger
from fastapi import APIRouter, Query

from app.db.session import DbSession
from app.schemas.message import MessageCreate, MessageRead, PaginatedMessages
from app.services.messages import create_message, get_messages_by_room

router = APIRouter()


@router.post("/messages", response_model=MessageRead, status_code=201)
def create_message_endpoint(
    data: MessageCreate,
    db: DbSession,
) -> MessageRead:
    """Create a new message.

    Args:
        data: Message creation data.
        db: Database session.

    Returns:
        The created message.
    """
    message = create_message(db, data)
    logger.info("Message created", extra={"message_id": message.id, "room_id": message.room_id})
    return MessageRead.model_validate(message)


@router.get("/rooms/{room_id}/messages", response_model=PaginatedMessages)
def get_room_messages(
    room_id: str,
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of messages to return"),
    offset: int = Query(default=0, ge=0, description="Number of messages to skip"),
) -> PaginatedMessages:
    """Get paginated messages for a room.

    Args:
        room_id: Room identifier.
        db: Database session.
        limit: Maximum number of messages to return (1-100).
        offset: Number of messages to skip.

    Returns:
        Paginated messages response.
    """
    messages, total = get_messages_by_room(db, room_id, limit, offset)
    logger.info("Retrieved room messages", extra={"room_id": room_id, "count": len(messages), "total": total})
    return PaginatedMessages(
        items=[MessageRead.model_validate(msg) for msg in messages],
        total=total,
        limit=limit,
        offset=offset,
    )
