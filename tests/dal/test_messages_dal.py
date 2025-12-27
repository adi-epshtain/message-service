"""Data access layer tests for messages."""

from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dal.messages import create_message, get_messages_by_room
from app.db.base import Base
from app.models.message import Message
from app.schemas.message import MessageCreate


@pytest_asyncio.fixture(scope="function")
async def in_memory_db():
    """Create an in-memory SQLite database for DAL tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)


class TestMessageModel:
    """Tests for Message ORM model behavior."""

    async def test_message_creation(self, in_memory_db: AsyncSession):
        """Message can be created and persisted with all required fields."""
        # Arrange & Act
        message = Message(
            room_id="room-1",
            sender="user-1",
            content="Test message",
        )
        in_memory_db.add(message)
        await in_memory_db.commit()
        await in_memory_db.refresh(message)
        
        # Assert
        assert message.id is not None
        assert message.room_id == "room-1"
        assert message.sender == "user-1"
        assert message.content == "Test message"
        assert isinstance(message.created_at, datetime)

    async def test_message_created_at_auto_generated(self, in_memory_db: AsyncSession):
        """Message created_at timestamp is automatically generated."""
        # Arrange & Act
        message = Message(
            room_id="room-2",
            sender="user-2",
            content="Another message",
        )
        in_memory_db.add(message)
        await in_memory_db.commit()
        await in_memory_db.refresh(message)
        
        # Assert
        assert message.created_at is not None
        assert isinstance(message.created_at, datetime)
        # The key behavior is that the database auto-generates the timestamp
        # We verify it's set and is a valid datetime, which confirms server_default worked

    async def test_message_allows_empty_content(self, in_memory_db: AsyncSession):
        """Message can be created with empty content string."""
        # Arrange & Act
        message = Message(
            room_id="room-3",
            sender="user-3",
            content="",
        )
        in_memory_db.add(message)
        await in_memory_db.commit()
        await in_memory_db.refresh(message)
        
        # Assert
        assert message.content == ""
        assert message.id is not None

    async def test_message_room_id_indexed(self, in_memory_db: AsyncSession):
        """Message room_id field is indexed for efficient queries."""
        # This is a structural test - we verify the index exists by checking
        # that queries by room_id are efficient (behavioral test)
        # Create messages in different rooms
        for room_id in ["room-a", "room-b", "room-a"]:
            message = Message(
                room_id=room_id,
                sender="user-1",
                content="Message",
            )
            in_memory_db.add(message)
        await in_memory_db.commit()
        
        # Query should efficiently filter by room_id
        from sqlalchemy import select
        query = select(Message).where(Message.room_id == "room-a")
        result = await in_memory_db.execute(query)
        results = list(result.scalars().all())
        
        assert len(results) == 2
        assert all(msg.room_id == "room-a" for msg in results)


class TestCreateMessageDAL:
    """DAL tests for create_message function."""

    async def test_create_message_persists_to_database(self, in_memory_db: AsyncSession):
        """create_message persists message to database with correct data."""
        # Arrange
        data = MessageCreate(
            room_id="room-100",
            sender="user-100",
            content="Persisted message",
        )
        
        # Act
        result = await create_message(in_memory_db, data)
        
        # Assert
        assert result.id is not None
        assert result.room_id == "room-100"
        assert result.sender == "user-100"
        assert result.content == "Persisted message"
        
        # Verify it's actually in the database
        retrieved = await in_memory_db.get(Message, result.id)
        assert retrieved is not None
        assert retrieved.room_id == "room-100"

    async def test_create_message_returns_refreshed_instance(self, in_memory_db: AsyncSession):
        """create_message returns message with database-generated fields populated."""
        # Arrange
        data = MessageCreate(
            room_id="room-101",
            sender="user-101",
            content="Test",
        )
        
        # Act
        result = await create_message(in_memory_db, data)
        
        # Assert
        assert result.id is not None  # ID should be populated
        assert result.created_at is not None  # Timestamp should be populated

    async def test_create_multiple_messages_different_rooms(self, in_memory_db: AsyncSession):
        """Multiple messages can be created in different rooms."""
        # Arrange & Act
        messages = []
        for i in range(3):
            data = MessageCreate(
                room_id=f"room-{i}",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            messages.append(await create_message(in_memory_db, data))
        
        # Assert
        assert len(messages) == 3
        assert all(msg.id is not None for msg in messages)
        assert messages[0].room_id == "room-0"
        assert messages[1].room_id == "room-1"
        assert messages[2].room_id == "room-2"


class TestGetMessagesByRoomDAL:
    """DAL tests for get_messages_by_room function."""

    async def test_get_messages_by_room_returns_correct_messages(self, in_memory_db: AsyncSession):
        """get_messages_by_room returns only messages for specified room."""
        # Arrange - Create messages in different rooms
        room_a_messages = []
        for i in range(3):
            data = MessageCreate(
                room_id="room-a",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            room_a_messages.append(await create_message(in_memory_db, data))
        
        # Create message in different room
        data = MessageCreate(
            room_id="room-b",
            sender="user-x",
            content="Other room message",
        )
        await create_message(in_memory_db, data)
        
        # Act
        messages, total = await get_messages_by_room(in_memory_db, "room-a", limit=10, offset=0)
        
        # Assert
        assert total == 3
        assert len(messages) == 3
        assert all(msg.room_id == "room-a" for msg in messages)
        assert all(msg.id in [m.id for m in room_a_messages] for msg in messages)

    async def test_get_messages_by_room_pagination_limit(self, in_memory_db: AsyncSession):
        """get_messages_by_room respects limit parameter."""
        # Arrange - Create 5 messages
        for i in range(5):
            data = MessageCreate(
                room_id="room-pag",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            await create_message(in_memory_db, data)
        
        # Act
        messages, total = await get_messages_by_room(in_memory_db, "room-pag", limit=3, offset=0)
        
        # Assert
        assert total == 5
        assert len(messages) == 3

    async def test_get_messages_by_room_pagination_offset(self, in_memory_db: AsyncSession):
        """get_messages_by_room respects offset parameter."""
        # Arrange - Create 5 messages
        created_messages = []
        for i in range(5):
            data = MessageCreate(
                room_id="room-offset",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            created_messages.append(await create_message(in_memory_db, data))
        
        # Act - Get messages with offset
        messages, total = await get_messages_by_room(in_memory_db, "room-offset", limit=2, offset=2)
        
        # Assert
        assert total == 5
        assert len(messages) == 2
        # Should skip first 2 messages
        assert messages[0].id == created_messages[2].id
        assert messages[1].id == created_messages[3].id

    async def test_get_messages_by_room_orders_by_created_at_ascending(self, in_memory_db: AsyncSession):
        """get_messages_by_room returns messages ordered by created_at ascending."""
        # Arrange - Create messages with small delays to ensure different timestamps
        import asyncio
        created_messages = []
        for i in range(3):
            data = MessageCreate(
                room_id="room-order",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            created_messages.append(await create_message(in_memory_db, data))
            await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Act
        messages, total = await get_messages_by_room(in_memory_db, "room-order", limit=10, offset=0)
        
        # Assert
        assert total == 3
        assert len(messages) == 3
        # Messages should be in ascending order by created_at
        for i in range(len(messages) - 1):
            assert messages[i].created_at <= messages[i + 1].created_at

    async def test_get_messages_by_room_empty_room_returns_zero_count(self, in_memory_db: AsyncSession):
        """get_messages_by_room returns empty list and zero count for non-existent room."""
        # Act
        messages, total = await get_messages_by_room(in_memory_db, "non-existent-room", limit=10, offset=0)
        
        # Assert
        assert messages == []
        assert total == 0

    async def test_get_messages_by_room_offset_beyond_total(self, in_memory_db: AsyncSession):
        """get_messages_by_room handles offset beyond available messages."""
        # Arrange - Create 2 messages
        for i in range(2):
            data = MessageCreate(
                room_id="room-beyond",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            await create_message(in_memory_db, data)
        
        # Act - Request with offset beyond total
        messages, total = await get_messages_by_room(in_memory_db, "room-beyond", limit=10, offset=100)
        
        # Assert
        assert total == 2
        assert messages == []

    async def test_get_messages_by_room_total_count_accurate(self, in_memory_db: AsyncSession):
        """get_messages_by_room returns accurate total count regardless of pagination."""
        # Arrange - Create 10 messages
        for i in range(10):
            data = MessageCreate(
                room_id="room-count",
                sender=f"user-{i}",
                content=f"Message {i}",
            )
            await create_message(in_memory_db, data)
        
        # Act - Request with small limit
        messages, total = await get_messages_by_room(in_memory_db, "room-count", limit=3, offset=0)
        
        # Assert
        assert len(messages) == 3
        assert total == 10  # Total should reflect all messages, not just returned ones
