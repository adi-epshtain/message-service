"""API-level tests for messages endpoints."""

import pytest
from fastapi import status


class TestCreateMessage:
    """Tests for POST /api/v1/messages endpoint."""

    def test_create_message_success(self, client):
        """Happy path: POST /api/v1/messages returns 201 and correct payload."""
        payload = {
            "room_id": "room-123",
            "sender": "user-1",
            "content": "Hello, world!",
        }
        response = client.post("/api/v1/messages", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["room_id"] == payload["room_id"]
        assert data["sender"] == payload["sender"]
        assert data["content"] == payload["content"]
        assert "id" in data
        assert "created_at" in data

    def test_create_message_missing_field(self, client):
        """Validation error: missing required field returns 422."""
        payload = {
            "room_id": "room-123",
            "sender": "user-1",
            # Missing 'content' field
        }
        response = client.post("/api/v1/messages", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_message_invalid_field_type(self, client):
        """Validation error: invalid field type returns 422."""
        payload = {
            "room_id": 123,  # Should be string
            "sender": "user-1",
            "content": "Hello, world!",
        }
        response = client.post("/api/v1/messages", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_message_empty_content(self, client):
        """Validation error: empty content should be allowed (valid string)."""
        payload = {
            "room_id": "room-123",
            "sender": "user-1",
            "content": "",
        }
        response = client.post("/api/v1/messages", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == ""


class TestGetRoomMessages:
    """Tests for GET /api/v1/rooms/{room_id}/messages endpoint."""

    def test_get_messages_with_pagination(self, client):
        """Read path: GET /api/v1/rooms/{room_id}/messages returns list with pagination."""
        # Create multiple messages
        room_id = "room-456"
        for i in range(5):
            client.post(
                "/api/v1/messages",
                json={
                    "room_id": room_id,
                    "sender": f"user-{i}",
                    "content": f"Message {i}",
                },
            )

        response = client.get(f"/api/v1/rooms/{room_id}/messages?limit=3&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["limit"] == 3
        assert data["offset"] == 0
        assert all("id" in item for item in data["items"])
        assert all("created_at" in item for item in data["items"])

    def test_get_messages_empty_result(self, client):
        """Edge case: pagination beyond available messages returns empty list (200)."""
        room_id = "room-789"
        # Create some messages
        client.post(
            "/api/v1/messages",
            json={
                "room_id": room_id,
                "sender": "user-1",
                "content": "Message 1",
            },
        )

        # Request with offset beyond available messages
        response = client.get(f"/api/v1/rooms/{room_id}/messages?limit=10&offset=100")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 1
        assert data["limit"] == 10
        assert data["offset"] == 100

    def test_get_messages_nonexistent_room(self, client):
        """Edge case: room with no messages returns 404."""
        response = client.get("/api/v1/rooms/nonexistent-room/messages")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_messages_default_pagination(self, client):
        """Default pagination parameters work correctly."""
        room_id = "room-default"
        client.post(
            "/api/v1/messages",
            json={
                "room_id": room_id,
                "sender": "user-1",
                "content": "Test message",
            },
        )

        response = client.get(f"/api/v1/rooms/{room_id}/messages")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["limit"] == 20  # Default limit
        assert data["offset"] == 0  # Default offset

