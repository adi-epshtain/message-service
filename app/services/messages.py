"""Message business logic services."""

from sqlalchemy.orm import Session

from app.dal.messages import create_message as dal_create_message, get_messages_by_room as dal_get_messages_by_room
from app.models.message import Message
from app.schemas.message import MessageCreate


def create_message(db: Session, data: MessageCreate) -> Message:
    """Create a new message.

    Args:
        db: Database session.
        data: Message creation data.

    Returns:
        The created message instance.
    """
    return dal_create_message(db, data)


def get_messages_by_room(
    db: Session, room_id: str, limit: int, offset: int
) -> tuple[list[Message], int]:
    """Get paginated messages for a room.

    Args:
        db: Database session.
        room_id: Room identifier to filter by.
        limit: Maximum number of messages to return.
        offset: Number of messages to skip.

    Returns:
        Tuple of (messages list, total count).
    """
    return dal_get_messages_by_room(db, room_id, limit, offset)
