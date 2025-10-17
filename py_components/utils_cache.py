import time
import logging
from typing import Any, Dict, Tuple, Optional

logger = logging.getLogger("crypto_dash")


class TTLCache:
    """Very small in-memory TTL cache for fetched objects."""

    def __init__(self, ttl_seconds: int = 600):
        self.ttl = int(ttl_seconds)
        self._store: Dict[str, Tuple[Any, float]] = {}

    def _is_valid(self, key: str) -> bool:
        if key not in self._store:
            return False
        _, ts = self._store[key]
        return (time.time() - ts) < self.ttl

    def get(self, key: str) -> Optional[Any]:
        if self._is_valid(key):
            logger.debug(f"[cache] hit: {key}")
            value, _ = self._store[key]
            return value
        if key in self._store:
            logger.debug(f"[cache] expired: {key}")
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.time())
        logger.debug(f"[cache] set: {key}")

    def clear(self) -> None:
        self._store.clear()
        logger.info("[cache] cleared")
