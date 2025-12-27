"""Message API endpoints."""

from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import logger
from fastapi import APIRouter, HTTPException, Query, status

from app.db.session import DbSession
from app.models import Message
from app.schemas.message import MessageCreate, MessageRead, PaginatedMessages
from app.services.messages import create_message, get_messages_by_room

router = APIRouter(prefix="/api/v1", tags=["messages"])


@router.post("/messages", response_model=MessageRead, status_code=201)
async def create_message_endpoint(
    data: MessageCreate,
    db: DbSession,
) -> MessageRead:
    """Create a new message.

    Args:
        data: Message creation data.
        db: Database session.

    Returns:
        The created message.

    Raises:
        HTTPException: If database error occurs.
    """
    try:
        message: Message = await create_message(db, data)
        logger.info("Message created", extra={"message_id": message.id, "room_id": message.room_id})
        return MessageRead.model_validate(message)
    except SQLAlchemyError as e:
        logger.error("Database error creating message", extra={"error": str(e)})
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message",
        )


@router.get("/rooms/{room_id}/messages", response_model=PaginatedMessages)
async def get_room_messages(
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
        Paginated messages response. Returns empty list if no messages found.

    Raises:
        HTTPException: If room does not exist (404) or database error occurs (500).
    """
    try:
        messages, total = await get_messages_by_room(db, room_id, limit, offset)
        
        # Optional: Return 404 if room has never had messages (first page, no results)
        if total == 0 and offset == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room '{room_id}' not found",
            )
        
        logger.info("Retrieved room messages", extra={"room_id": room_id, "count": len(messages), "total": total})
        return PaginatedMessages(
            items=[MessageRead.model_validate(msg) for msg in messages],
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error retrieving messages", extra={"room_id": room_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages",
        )
