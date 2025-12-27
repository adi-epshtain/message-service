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
        
        # Mock DAL function
        with patch("app.services.messages.dal_create_message", return_value=mock_message) as mock_dal:
            data = MessageCreate(
                room_id="room-123",
                sender="user-1",
                content="Hello, world!",
            )
            
            # Act
            result = create_message(mock_db, data)
            
            # Assert
            assert result == mock_message
            mock_dal.assert_called_once_with(mock_db, data)

    def test_create_message_with_empty_content(self):
        """Service allows creating message with empty content."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_message = MagicMock(spec=Message)
        mock_message.id = 2
        mock_message.content = ""
        
        with patch("app.services.messages.dal_create_message", return_value=mock_message):
            data = MessageCreate(
                room_id="room-456",
                sender="user-2",
                content="",
            )
            
            # Act
            result = create_message(mock_db, data)
            
            # Assert
            assert result == mock_message

    def test_create_message_calls_dal(self):
        """Service delegates to DAL layer."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_message = MagicMock(spec=Message)
        
        with patch("app.services.messages.dal_create_message", return_value=mock_message) as mock_dal:
            data = MessageCreate(
                room_id="room-789",
                sender="user-3",
                content="Test content",
            )
            
            # Act
            result = create_message(mock_db, data)
            
            # Assert
            assert result == mock_message
            mock_dal.assert_called_once_with(mock_db, data)


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
        
        with patch("app.services.messages.dal_get_messages_by_room", return_value=(mock_messages, 5)) as mock_dal:
            # Act
            messages, total = get_messages_by_room(mock_db, "room-1", limit=3, offset=0)
            
            # Assert
            assert messages == mock_messages
            assert total == 5
            mock_dal.assert_called_once_with(mock_db, "room-1", 3, 0)

    def test_get_messages_by_room_with_offset(self):
        """Service correctly applies offset for pagination."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_messages = [MagicMock(spec=Message, id=4, room_id="room-1")]
        
        with patch("app.services.messages.dal_get_messages_by_room", return_value=(mock_messages, 5)) as mock_dal:
            # Act
            messages, total = get_messages_by_room(mock_db, "room-1", limit=3, offset=3)
            
            # Assert
            assert len(messages) == 1
            assert total == 5
            mock_dal.assert_called_once_with(mock_db, "room-1", 3, 3)

    def test_get_messages_by_room_empty_room(self):
        """Service returns empty list and zero count for room with no messages."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        
        with patch("app.services.messages.dal_get_messages_by_room", return_value=([], 0)) as mock_dal:
            # Act
            messages, total = get_messages_by_room(mock_db, "empty-room", limit=10, offset=0)
            
            # Assert
            assert messages == []
            assert total == 0
            mock_dal.assert_called_once_with(mock_db, "empty-room", 10, 0)

    def test_get_messages_by_room_filters_by_room_id(self):
        """Service delegates room filtering to DAL."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        
        with patch("app.services.messages.dal_get_messages_by_room", return_value=([], 0)) as mock_dal:
            # Act
            get_messages_by_room(mock_db, "specific-room", limit=20, offset=0)
            
            # Assert
            mock_dal.assert_called_once_with(mock_db, "specific-room", 20, 0)

    def test_get_messages_by_room_calls_dal(self):
        """Service delegates to DAL when getting messages by room."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        
        with patch("app.services.messages.dal_get_messages_by_room", return_value=([], 0)) as mock_dal:
            # Act
            get_messages_by_room(mock_db, "room-1", limit=10, offset=0)
            
            # Assert
            mock_dal.assert_called_once_with(mock_db, "room-1", 10, 0)
