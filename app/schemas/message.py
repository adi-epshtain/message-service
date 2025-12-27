"""Message Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    room_id: str = Field(..., min_length=1, max_length=100, description="Room identifier")
    sender: str = Field(..., min_length=1, max_length=100, description="Message sender")
    content: str = Field(..., max_length=5000, description="Message content")

    model_config = ConfigDict(from_attributes=True)


class MessageRead(BaseModel):
    """Schema for reading a message."""

    id: int
    room_id: str
    sender: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedMessages(BaseModel):
    """Schema for paginated message responses."""

    items: list[MessageRead]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
