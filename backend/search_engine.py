"""Web search and information retrieval engine with offline support."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class SearchCache:
    """Cache search results for offline access."""

    def __init__(self, max_age_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_age_hours = max_age_hours

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().encode()).hexdigest()

    def get(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        key = self._get_cache_key(query)
        if key in self.cache:
            cached_data = self.cache[key]
            age = (datetime.now() - cached_data["timestamp"]).total_seconds() / 3600

            if age < self.max_age_hours:
                logger.info(f"Cache hit for query: {query}")
                return cached_data["results"]
            else:
                del self.cache[key]
        return None

    def set(self, query: str, results: List[Dict[str, Any]]):
        """Cache search results."""
        key = self._get_cache_key(query)
        self.cache[key] = {
            "results": results,
            "timestamp": datetime.now(),
            "query": query,
        }

    def clear_expired(self):
        """Clear expired cache entries."""
        now = datetime.now()
        expired_keys = [
            key
            for key, data in self.cache.items()
            if (now - data["timestamp"]).total_seconds() / 3600 > self.max_age_hours
        ]
        for key in expired_keys:
            del self.cache[key]


class SearchEngine:
    """Search engine with autonomous and on-demand capabilities."""

    def __init__(self, enable_web_search: bool = True):
        self.enable_web_search = enable_web_search
        self.cache = SearchCache()
        self.search_history: List[Dict[str, Any]] = []

    def autonomous_search_decision(
        self, message: str, context: List[Dict[str, str]]
    ) -> tuple[bool, Optional[str]]:
        """Decide if autonomous search is needed and what to search for."""
        keywords = [
            "latest",
            "current",
            "today",
            "recent",
            "real-time",
            "now",
            "what is",
            "how to",
            "find",
            "search",
            "tell me about",
            "information about",
            "news",
            "update",
        ]

        lower_message = message.lower()

        # Check if message contains search keywords
        has_search_keyword = any(kw in lower_message for kw in keywords)

        # Check if question is open-ended or requires current information
        is_question = message.strip().endswith("?")
        might_need_info = any(
            term in lower_message
            for term in ["who", "what", "where", "when", "why", "how"]
        )

        if has_search_keyword or (is_question and might_need_info):
            # Extract potential search query
            search_query = self._extract_search_query(message)
            if search_query:
                return True, search_query

        return False, None

    def _extract_search_query(self, message: str) -> Optional[str]:
        """Extract search query from message."""
        # Remove common question words and punctuation
        question_words = [
            "what is",
            "how to",
            "tell me about",
            "search for",
            "find",
            "information about",
            "news about",
            "latest",
        ]

        cleaned = message.lower().strip()

        for qw in question_words:
            if cleaned.startswith(qw):
                cleaned = cleaned[len(qw) :].strip()
                break

        # Remove trailing question mark
        cleaned = cleaned.rstrip("?").strip()

        # Only return if we have meaningful content
        if len(cleaned) > 3:
            return cleaned
        return None

    def search(
        self,
        query: str,
        autonomous: bool = False,
        use_cache: bool = True,
        offline_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform search.

        Args:
            query: Search query
            autonomous: Whether search was autonomous or user-requested
            use_cache: Use cached results if available
            offline_mode: Only use cached/local results

        Returns:
            Search result with metadata
        """
        logger.info(
            f"Search: '{query}' (autonomous={autonomous}, offline={offline_mode})"
        )

        # Check cache first
        if use_cache:
            cached_results = self.cache.get(query)
            if cached_results:
                return {
                    "query": query,
                    "results": cached_results,
                    "source": "cache",
                    "autonomous": autonomous,
                    "timestamp": datetime.now().isoformat(),
                }

        # If offline mode, only return cached results
        if offline_mode:
            logger.warning(f"Offline mode: No results for '{query}'")
            return {
                "query": query,
                "results": [],
                "source": "offline",
                "autonomous": autonomous,
                "timestamp": datetime.now().isoformat(),
                "message": "Offline mode - no internet connection",
            }

        # Perform web search (simulated)
        results = self._perform_web_search(query)

        # Cache results
        if results:
            self.cache.set(query, results)

        search_result = {
            "query": query,
            "results": results,
            "source": "web",
            "autonomous": autonomous,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(results),
        }

        # Record in history
        self.search_history.append(search_result)

        return search_result

    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform actual web search.

        Note: In production, integrate with:
        - DuckDuckGo API
        - Google Search API
        - Bing Search API
        - Or web scraping with BeautifulSoup
        """
        try:
            # TODO: Integrate actual web search API
            # For now, return mock results
            mock_results = [
                {
                    "title": f"Result 1: {query}",
                    "url": f"https://example.com/search?q={query}",
                    "snippet": f"Information about {query}",
                    "source": "example.com",
                }
            ]
            return mock_results
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history."""
        return self.search_history[-limit:]

    def enable_offline_mode(self):
        """Switch to offline mode (cache only)."""
        logger.info("Offline mode enabled")
        self.enable_web_search = False

    def disable_offline_mode(self):
        """Switch to online mode."""
        logger.info("Offline mode disabled")
        self.enable_web_search = True

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_queries": len(self.cache.cache),
            "total_searches": len(self.search_history),
            "cache_size_bytes": sum(
                len(json.dumps(data)) for data in self.cache.cache.values()
            ),
        }
