"""User and session management with sandboxing."""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class UserSandbox:
    """Isolated sandbox for each user."""

    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self.created_at = datetime.now()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.data_store: Dict[str, Any] = {}
        self.search_history: List[Dict[str, Any]] = []
        self.preferences: Dict[str, Any] = {
            "auto_search": True,
            "offline_mode": False,
            "max_searches_per_session": 10,
            "search_timeout_seconds": 30,
        }

    def create_session(self) -> str:
        """Create new session within user's sandbox."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "messages": [],
            "state": {},
            "search_queries": [],
            "offline": False,
        }
        logger.info(f"Session created for user {self.username}: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from user's sandbox."""
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to session."""
        session = self.get_session(session_id)
        if not session:
            return False

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        session["messages"].append(message)
        return True

    def add_search_query(self, session_id: str, query: str, results: List[Dict], source: str):
        """Record search query and results."""
        session = self.get_session(session_id)
        if not session:
            return False

        search_record = {
            "query": query,
            "results": results,
            "source": source,  # "web", "local", "cache", "autonomous"
            "timestamp": datetime.now().isoformat(),
            "result_count": len(results),
        }
        session["search_queries"].append(search_record)
        self.search_history.append(search_record)
        return True

    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get full session history."""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session_id,
            "user_id": self.user_id,
            "username": self.username,
            "created_at": session["created_at"].isoformat(),
            "messages": session["messages"],
            "search_queries": session["search_queries"],
            "offline": session.get("offline", False),
        }

    def delete_session(self, session_id: str) -> bool:
        """Delete session from user's sandbox."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session deleted for user {self.username}: {session_id}")
            return True
        return False

    def set_offline_mode(self, session_id: str, offline: bool):
        """Set offline mode for session."""
        session = self.get_session(session_id)
        if session:
            session["offline"] = offline

    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences."""
        self.preferences.update(preferences)

    def get_stats(self) -> Dict[str, Any]:
        """Get user sandbox statistics."""
        total_messages = sum(
            len(s["messages"]) for s in self.sessions.values()
        )
        total_searches = len(self.search_history)

        return {
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "total_sessions": len(self.sessions),
            "total_messages": total_messages,
            "total_searches": total_searches,
            "active_sessions": [s_id for s_id, s in self.sessions.items()
                               if (datetime.now() - s["created_at"]).seconds < 3600],
        }


class UserManager:
    """Manage users and their sandboxes."""

    def __init__(self):
        self.users: Dict[str, UserSandbox] = {}
        self.user_sessions: Dict[str, str] = {}  # session_id -> user_id mapping
        self.session_timeout = 3600  # 1 hour

    def create_user(self, username: str, email: str = None) -> str:
        """Create new user sandbox."""
        user_id = str(uuid.uuid4())
        self.users[user_id] = UserSandbox(user_id, username)
        logger.info(f"User created: {username} ({user_id})")
        return user_id

    def get_user(self, user_id: str) -> Optional[UserSandbox]:
        """Get user sandbox."""
        return self.users.get(user_id)

    def create_user_session(self, user_id: str) -> Optional[str]:
        """Create session within user's sandbox."""
        user = self.get_user(user_id)
        if not user:
            return None

        session_id = user.create_session()
        self.user_sessions[session_id] = user_id
        return session_id

    def get_session_user(self, session_id: str) -> Optional[str]:
        """Get user ID from session."""
        return self.user_sessions.get(session_id)

    def add_message_to_session(
        self, session_id: str, role: str, content: str, metadata: Dict = None
    ) -> bool:
        """Add message to session."""
        user_id = self.get_session_user(session_id)
        if not user_id:
            return False

        user = self.get_user(user_id)
        if not user:
            return False

        return user.add_message(session_id, role, content, metadata)

    def record_search(
        self, session_id: str, query: str, results: List[Dict], source: str
    ) -> bool:
        """Record search in user's sandbox."""
        user_id = self.get_session_user(session_id)
        if not user_id:
            return False

        user = self.get_user(user_id)
        if not user:
            return False

        return user.add_search_query(session_id, query, results, source)

    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get session history."""
        user_id = self.get_session_user(session_id)
        if not user_id:
            return {"error": "Session not found"}

        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}

        return user.get_session_history(session_id)

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (GDPR compliance)."""
        if user_id in self.users:
            user = self.users[user_id]
            # Remove all user's sessions from mapping
            for session_id in list(self.user_sessions.keys()):
                if self.user_sessions[session_id] == user_id:
                    del self.user_sessions[session_id]
            # Remove user sandbox
            del self.users[user_id]
            logger.info(f"User deleted: {user_id}")
            return True
        return False

    def get_all_user_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all users."""
        return {user_id: user.get_stats() for user_id, user in self.users.items()}
