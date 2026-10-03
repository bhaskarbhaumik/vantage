"""Per-provider concurrency limiting + retry with backoff on transient errors."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


class RateLimiter:
    """A concurrency gate (semaphore) plus exponential-backoff retry."""

    def __init__(self, max_concurrency: int = 8, max_attempts: int = 5,
                 retry_min_seconds: float = 2, retry_max_seconds: float = 30) -> None:
        self._sem = asyncio.Semaphore(max_concurrency)
        self._max_attempts = max_attempts
        self._retry_min = retry_min_seconds
        self._retry_max = retry_max_seconds

    async def run(self, fn: Callable[[], Awaitable[T]]) -> T:
        @retry(
            reraise=True,
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(multiplier=1, min=self._retry_min, max=self._retry_max),
            retry=retry_if_exception_type(_TRANSIENT),
        )
        async def _guarded() -> T:
            async with self._sem:
                return await fn()

        return await _guarded()


# Broad transient set; provider SDKs raise their own rate-limit/timeout types which subclass these.
_TRANSIENT: tuple[type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
)


def register_transient(*exc_types: type[Exception]) -> None:
    """Providers call this at import to widen the retryable set with their SDK error types."""
    global _TRANSIENT
    _TRANSIENT = tuple({*_TRANSIENT, *exc_types})
