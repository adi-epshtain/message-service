"""Data access layer for message database operations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate


def create_message(db: Session, data: MessageCreate) -> Message:
    """Create and persist a new message.

    Args:
        db: Database session.
        data: Message creation data.

    Returns:
        The created message instance.
    """
    message = Message(
        room_id=data.room_id,
        sender=data.sender,
        content=data.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


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
    # Get total count
    count_query = select(func.count()).select_from(Message).where(Message.room_id == room_id)
    total = db.scalar(count_query)

    # Get paginated messages ordered by created_at ascending
    messages_query = (
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    messages = list(db.scalars(messages_query).all())

    return messages, total

