"""Persistence layer for conversation state."""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from .config import settings
from .models import ConversationStateData

try:
    import redis.asyncio as redis  # type: ignore
except ImportError:  # pragma: no cover - redis optional in tests
    redis = None


logger = logging.getLogger(__name__)


class ConversationStateStore:
    """Persist conversation state in Redis with in-memory fallback."""

    def __init__(self):
        self._ttl_seconds = settings.session_timeout_hours * 3600
        self._memory_store: Dict[str, str] = {}
        self._memory_lock = asyncio.Lock()
        self._redis = None
        self._redis_available = False

        if redis is not None:
            try:
                self._redis = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                self._redis_available = True
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Failed to initialize Redis client: %s", exc)
                self._redis = None
                self._redis_available = False

    @staticmethod
    def _key(phone: str) -> str:
        return f"conversation_state:{phone}"

    async def get(self, phone: str) -> Optional[ConversationStateData]:
        data = None

        if self._redis_available and self._redis is not None:
            try:
                data = await self._redis.get(self._key(phone))
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Redis get failed, switching to memory store: %s", exc)
                self._redis_available = False
                data = None

        if data is None:
            async with self._memory_lock:
                data = self._memory_store.get(phone)

        if not data:
            return None

        return ConversationStateData.model_validate_json(data)

    async def set(self, phone: str, state: ConversationStateData):
        payload = state.model_dump_json()

        if self._redis_available and self._redis is not None:
            try:
                await self._redis.set(
                    self._key(phone),
                    payload,
                    ex=self._ttl_seconds
                )
                return
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Redis set failed, falling back to memory store: %s", exc)
                self._redis_available = False

        async with self._memory_lock:
            self._memory_store[phone] = payload

    async def delete(self, phone: str):
        if self._redis_available and self._redis is not None:
            try:
                await self._redis.delete(self._key(phone))
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Redis delete failed, falling back to memory store: %s", exc)
                self._redis_available = False

        async with self._memory_lock:
            self._memory_store.pop(phone, None)


# Global store instance
state_store = ConversationStateStore()

