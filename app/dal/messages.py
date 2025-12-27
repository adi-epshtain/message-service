"""Data access layer for message database operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.schemas.message import MessageCreate


async def create_message(db: AsyncSession, data: MessageCreate) -> Message:
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
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages_by_room(
    db: AsyncSession, room_id: str, limit: int, offset: int
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
    result = await db.execute(count_query)
    total = result.scalar_one()

    # Get paginated messages ordered by created_at ascending
    messages_query = (
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(messages_query)
    messages = list(result.scalars().all())

    return messages, total

