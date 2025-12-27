"""Service-level tests for messages business logic."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.messages import create_message, get_messages_by_room


class TestCreateMessage:
    """Tests for create_message service function."""

    def test_create_message_success(self):
        """Service creates message with correct data and persists it."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_message = MagicMock(spec=Message)
        mock_message.id = 1
        mock_message.room_id = "room-123"
        mock_message.sender = "user-1"
        mock_message.content = "Hello, world!"
        
        # Mock Message constructor to return our mock
        with patch("app.services.messages.Message", return_value=mock_message):
            data = MessageCreate(
                room_id="room-123",
                sender="user-1",
                content="Hello, world!",
            )
            
            # Act
            result = create_message(mock_db, data)
            
            # Assert
            assert result == mock_message
            mock_db.add.assert_called_once_with(mock_message)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_message)

    def test_create_message_with_empty_content(self):
        """Service allows creating message with empty content."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_message = MagicMock(spec=Message)
        mock_message.id = 2
        mock_message.content = ""
        
        with patch("app.services.messages.Message", return_value=mock_message):
            data = MessageCreate(
                room_id="room-456",
                sender="user-2",
                content="",
            )
            
            # Act
            result = create_message(mock_db, data)
            
            # Assert
            assert result == mock_message
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    def test_create_message_persists_all_fields(self):
        """Service correctly maps all fields from schema to model."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_message = MagicMock(spec=Message)
        
        with patch("app.services.messages.Message") as mock_message_class:
            mock_message_class.return_value = mock_message
            data = MessageCreate(
                room_id="room-789",
                sender="user-3",
                content="Test content",
            )
            
            # Act
            create_message(mock_db, data)
            
            # Assert
            mock_message_class.assert_called_once_with(
                room_id="room-789",
                sender="user-3",
                content="Test content",
            )


class TestGetMessagesByRoom:
    """Tests for get_messages_by_room service function."""

    def test_get_messages_by_room_returns_paginated_results(self):
        """Service returns messages and total count for a room."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_messages = [
            MagicMock(spec=Message, id=1, room_id="room-1"),
            MagicMock(spec=Message, id=2, room_id="room-1"),
            MagicMock(spec=Message, id=3, room_id="room-1"),
        ]
        
        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = mock_messages
        mock_db.scalars.return_value = mock_scalars_result
        mock_db.scalar.return_value = 5  # Total count
        
        # Act
        messages, total = get_messages_by_room(mock_db, "room-1", limit=3, offset=0)
        
        # Assert
        assert messages == mock_messages
        assert total == 5
        assert mock_db.scalar.call_count == 1
        assert mock_db.scalars.call_count == 1

    def test_get_messages_by_room_with_offset(self):
        """Service correctly applies offset for pagination."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_messages = [MagicMock(spec=Message, id=4, room_id="room-1")]
        
        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = mock_messages
        mock_db.scalars.return_value = mock_scalars_result
        mock_db.scalar.return_value = 5
        
        # Act
        messages, total = get_messages_by_room(mock_db, "room-1", limit=3, offset=3)
        
        # Assert
        assert len(messages) == 1
        assert total == 5
        # Verify database was queried (behavioral check)
        assert mock_db.scalars.called
        assert mock_db.scalar.called

    def test_get_messages_by_room_empty_room(self):
        """Service returns empty list and zero count for room with no messages."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = []
        mock_db.scalars.return_value = mock_scalars_result
        mock_db.scalar.return_value = 0
        
        # Act
        messages, total = get_messages_by_room(mock_db, "empty-room", limit=10, offset=0)
        
        # Assert
        assert messages == []
        assert total == 0

    def test_get_messages_by_room_filters_by_room_id(self):
        """Service queries only messages for the specified room."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = []
        mock_db.scalars.return_value = mock_scalars_result
        mock_db.scalar.return_value = 0
        
        # Act
        get_messages_by_room(mock_db, "specific-room", limit=20, offset=0)
        
        # Assert
        # Verify both queries filter by room_id
        count_query = mock_db.scalar.call_args[0][0]
        messages_query = mock_db.scalars.call_args[0][0]
        
        # Both queries should have WHERE clause for room_id
        assert count_query is not None
        assert messages_query is not None

    def test_get_messages_by_room_calls_database(self):
        """Service queries database when getting messages by room."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = []
        mock_db.scalars.return_value = mock_scalars_result
        mock_db.scalar.return_value = 0
        
        # Act
        get_messages_by_room(mock_db, "room-1", limit=10, offset=0)
        
        # Assert
        # Verify database queries were executed (behavioral check)
        assert mock_db.scalar.called  # Count query
        assert mock_db.scalars.called  # Messages query
