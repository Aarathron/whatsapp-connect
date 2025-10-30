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
    """Persist conversation state in Redis with an explicit memory-only opt-in."""

    def __init__(self):
        self._ttl_seconds = settings.session_timeout_hours * 3600
        self._memory_store: Dict[str, str] = {}
        self._memory_lock = asyncio.Lock()
        self._redis = None
        self._redis_available = False
        self._memory_warning_logged = False
        self._memory_only_mode = False
        self._initialized = False
        self._init_lock = asyncio.Lock()

        self._redis_module_available = redis is not None
        self._allow_memory = bool(settings.allow_memory_state_store)
        self._redis_url = settings.redis_url

    async def initialize(self):
        """Establish Redis connectivity or intentionally fall back to memory."""
        if self._initialized:
            return

        async with self._init_lock:
            if self._initialized:
                return

            if not self._redis_module_available:
                if not self._allow_memory:
                    self._log_memory_fallback(
                        "redis.asyncio package not available; cannot provide shared state store"
                    )
                    raise RuntimeError(
                        "Redis support is required for conversation state persistence."
                    )

                self._memory_only_mode = True
                self._initialized = True
                self._log_memory_fallback(
                    "redis.asyncio package not available; using in-memory fallback"
                )
                return

            try:
                self._redis = redis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._redis.ping()

                self._redis_available = True
                self._initialized = True
                logger.info(
                    "Connected to Redis for conversation state (ttl=%s seconds)",
                    self._ttl_seconds
                )
            except Exception as exc:  # pragma: no cover - depends on env
                logger.error(
                    "Failed to connect to Redis at %s: %s",
                    self._redis_url,
                    exc
                )
                self._redis = None
                self._redis_available = False

                if not self._allow_memory:
                    self._log_memory_fallback(
                        "Redis connection failed during initialization"
                    )
                    raise RuntimeError(
                        "Redis state store required but connection failed"
                    ) from exc

                self._memory_only_mode = True
                self._initialized = True
                self._log_memory_fallback(
                    "Redis connection failed during initialization; using in-memory fallback"
                )

    async def _ensure_ready(self):
        if not self._initialized:
            await self.initialize()

    def _log_memory_fallback(self, reason: str):
        if self._memory_warning_logged:
            return

        logger.error(
            "Conversation state persistence degraded: %s. "
            "Per-process memory store will drop state across workers.",
            reason
        )
        self._memory_warning_logged = True

    @staticmethod
    def _key(phone: str) -> str:
        return f"conversation_state:{phone}"

    async def get(self, phone: str) -> Optional[ConversationStateData]:
        await self._ensure_ready()
        data = None

        if self._redis_available and self._redis is not None:
            try:
                data = await self._redis.get(self._key(phone))
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Redis get failed, switching to memory store: %s", exc)
                self._redis_available = False
                self._memory_only_mode = True
                self._log_memory_fallback("Redis get failed")
                data = None

        if data is None:
            async with self._memory_lock:
                data = self._memory_store.get(phone)

        if not data:
            return None

        return ConversationStateData.model_validate_json(data)

    async def set(self, phone: str, state: ConversationStateData):
        await self._ensure_ready()
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
                self._memory_only_mode = True
                self._log_memory_fallback("Redis set failed")

        async with self._memory_lock:
            self._memory_store[phone] = payload

        if not self._redis_available:
            self._log_memory_fallback("Redis unavailable during set operation")

    async def delete(self, phone: str):
        await self._ensure_ready()
        if self._redis_available and self._redis is not None:
            try:
                await self._redis.delete(self._key(phone))
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Redis delete failed, falling back to memory store: %s", exc)
                self._redis_available = False
                self._memory_only_mode = True
                self._log_memory_fallback("Redis delete failed")

        async with self._memory_lock:
            self._memory_store.pop(phone, None)

        if not self._redis_available:
            self._log_memory_fallback("Redis unavailable during delete operation")

    @property
    def uses_memory_only(self) -> bool:
        return self._memory_only_mode


# Global store instance
state_store = ConversationStateStore()

