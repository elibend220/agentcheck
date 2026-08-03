"""Tests for JARVIS AGI Backend Server."""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)


class TestSystemEndpoints:
    """Test system endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "JARVIS" in data["name"]
        assert "version" in data

    def test_status_endpoint(self):
        """Test status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["version"] == "1.0.0"
        assert data["phases_enabled"] == 23
        assert "uptime_seconds" in data
        assert "sessions_active" in data

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestSessionEndpoints:
    """Test session management endpoints."""

    def test_create_session(self):
        """Test session creation."""
        response = client.post("/session/create")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        session_id = data["session_id"]
        assert len(session_id) > 0

    def test_get_session_info(self):
        """Test getting session information."""
        # Create session
        create_response = client.post("/session/create")
        session_id = create_response.json()["session_id"]

        # Get session info
        response = client.get(f"/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "created_at" in data
        assert data["message_count"] == 0

    def test_get_nonexistent_session(self):
        """Test getting nonexistent session."""
        response = client.get("/session/nonexistent-session-id")
        assert response.status_code == 404

    def test_get_session_history(self):
        """Test getting session history."""
        # Create session
        create_response = client.post("/session/create")
        session_id = create_response.json()["session_id"]

        # Get history (should be empty)
        response = client.get(f"/session/{session_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert len(data["messages"]) == 0


class TestChatEndpoint:
    """Test chat endpoint."""

    def test_chat_with_new_session(self):
        """Test chat with automatic session creation."""
        response = client.post(
            "/chat",
            json={"message": "Hello JARVIS"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert "response" in data
        assert "consciousness_level" in data
        assert "emergence_level" in data
        assert "confidence_score" in data
        assert "execution_time_ms" in data
        assert "timestamp" in data
        assert "phases_executed" in data

    def test_chat_with_existing_session(self):
        """Test chat with existing session."""
        # Create session
        create_response = client.post("/session/create")
        session_id = create_response.json()["session_id"]

        # Send message
        response = client.post(
            "/chat",
            json={
                "session_id": session_id,
                "message": "What are your capabilities?"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["message"] == "What are your capabilities?"

    def test_chat_with_phase_config(self):
        """Test chat with custom phase configuration."""
        response = client.post(
            "/chat",
            json={
                "message": "Test message",
                "enable_phases": {
                    "enable_phase19": True,
                    "enable_phase20": False,
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_chat_empty_message(self):
        """Test chat with empty message."""
        response = client.post(
            "/chat",
            json={"message": ""}
        )
        # Should either return 200 or 400
        assert response.status_code in [200, 400]

    def test_chat_long_message(self):
        """Test chat with long message."""
        long_message = "Test " * 1000  # 5000 chars
        response = client.post(
            "/chat",
            json={"message": long_message}
        )
        assert response.status_code == 200

    def test_chat_special_characters(self):
        """Test chat with special characters."""
        response = client.post(
            "/chat",
            json={"message": "שלום JARVIS! 你好 🌟"}
        )
        assert response.status_code == 200


class TestResponseFormats:
    """Test response format compliance."""

    def test_chat_response_format(self):
        """Test chat response has correct format."""
        response = client.post(
            "/chat",
            json={"message": "Test format"}
        )
        assert response.status_code == 200
        data = response.json()

        # Verify all required fields
        required_fields = [
            "session_id", "message", "response",
            "phases_executed", "consciousness_level",
            "emergence_level", "confidence_score",
            "execution_time_ms", "timestamp"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify field types
        assert isinstance(data["session_id"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["phases_executed"], list)
        assert isinstance(data["consciousness_level"], (int, float))
        assert isinstance(data["emergence_level"], (int, float))
        assert isinstance(data["confidence_score"], (int, float))
        assert isinstance(data["execution_time_ms"], (int, float))
        assert isinstance(data["timestamp"], str)

        # Verify value ranges
        assert 0.0 <= data["consciousness_level"] <= 1.0
        assert 0.0 <= data["emergence_level"] <= 1.0
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert data["execution_time_ms"] >= 0

    def test_status_response_format(self):
        """Test status response format."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["status", "version", "phases_enabled", "uptime_seconds", "sessions_active"]
        for field in required_fields:
            assert field in data

        assert data["status"] == "online"
        assert isinstance(data["phases_enabled"], int)
        assert data["phases_enabled"] == 23


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_session_id_format(self):
        """Test with invalid session ID."""
        response = client.get("/session/invalid@@id")
        assert response.status_code == 404

    def test_missing_message_field(self):
        """Test chat without message field."""
        response = client.post("/chat", json={})
        # Should return validation error
        assert response.status_code in [422, 400]


class TestConcurrency:
    """Test concurrent operations."""

    def test_multiple_sessions(self):
        """Test multiple concurrent sessions."""
        sessions = []
        for i in range(5):
            response = client.post("/session/create")
            assert response.status_code == 200
            sessions.append(response.json()["session_id"])

        # Verify all sessions are unique
        assert len(sessions) == len(set(sessions))

        # Send messages in all sessions
        for session_id in sessions:
            response = client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "message": f"Test message for {session_id}"
                }
            )
            assert response.status_code == 200

    def test_rapid_messages(self):
        """Test rapid message sending."""
        session_response = client.post("/session/create")
        session_id = session_response.json()["session_id"]

        for i in range(3):
            response = client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "message": f"Message {i}"
                }
            )
            assert response.status_code == 200

        # Verify history contains all messages
        history_response = client.get(f"/session/{session_id}/history")
        history = history_response.json()["messages"]
        # Should have 3 user messages + 3 assistant responses = 6 total
        assert len(history) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
