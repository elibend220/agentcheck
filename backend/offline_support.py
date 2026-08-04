"""Offline mode support for JARVIS backend."""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class OfflineStorage:
    """Local storage for offline mode support."""

    def __init__(self, db_path: str = "jarvis_offline.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize offline database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Messages table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """
            )

            # Search results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS search_cache (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL UNIQUE,
                    results TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT
                )
            """
            )

            # Sync queue table (for when connection is restored)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info(f"Offline database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize offline database: {e}")

    def save_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        message_id: str,
    ) -> bool:
        """Save message for offline access."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO messages (id, user_id, session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (message_id, user_id, session_id, role, content, datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session from offline storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, role, content, timestamp FROM messages WHERE session_id = ?",
                (session_id,),
            )

            messages = []
            for row in cursor.fetchall():
                messages.append(
                    {
                        "id": row[0],
                        "role": row[1],
                        "content": row[2],
                        "timestamp": row[3],
                    }
                )

            conn.close()
            return messages
        except Exception as e:
            logger.error(f"Failed to get session messages: {e}")
            return []

    def cache_search_result(self, query: str, results: List[Dict[str, Any]], source: str) -> bool:
        """Cache search results for offline access."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO search_cache (id, query, results, timestamp, source)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    query,
                    query,
                    json.dumps(results),
                    datetime.now().isoformat(),
                    source,
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to cache search result: {e}")
            return False

    def get_cached_search(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search result."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT results FROM search_cache WHERE query = ?", (query,)
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get cached search: {e}")
            return None

    def queue_sync_action(
        self, user_id: str, session_id: str, action: str, data: Dict[str, Any], action_id: str
    ) -> bool:
        """Queue action for sync when connection is restored."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO sync_queue (id, user_id, session_id, action, data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    action_id,
                    user_id,
                    session_id,
                    action,
                    json.dumps(data),
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to queue sync action: {e}")
            return False

    def get_pending_syncs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending sync actions for user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, session_id, action, data, timestamp
                FROM sync_queue
                WHERE user_id = ? AND synced = 0
                ORDER BY timestamp ASC
            """,
                (user_id,),
            )

            actions = []
            for row in cursor.fetchall():
                actions.append(
                    {
                        "id": row[0],
                        "session_id": row[1],
                        "action": row[2],
                        "data": json.loads(row[3]),
                        "timestamp": row[4],
                    }
                )

            conn.close()
            return actions
        except Exception as e:
            logger.error(f"Failed to get pending syncs: {e}")
            return []

    def mark_synced(self, action_id: str) -> bool:
        """Mark sync action as completed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE sync_queue SET synced = 1 WHERE id = ?", (action_id,)
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to mark synced: {e}")
            return False

    def get_offline_stats(self) -> Dict[str, Any]:
        """Get offline storage statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM messages")
            message_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM search_cache")
            cache_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = 0")
            pending_syncs = cursor.fetchone()[0]

            conn.close()

            return {
                "offline_messages": message_count,
                "cached_searches": cache_count,
                "pending_syncs": pending_syncs,
                "db_file": self.db_path,
            }
        except Exception as e:
            logger.error(f"Failed to get offline stats: {e}")
            return {}
