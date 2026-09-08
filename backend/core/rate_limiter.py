"""
backend.core.rate_limiter - Gemini API call rate limiter.

Implements a thread-safe sliding-window rate limiter that enforces:
  - RPM  (requests per minute)   e.g. Gemini Free Tier: 15 RPM
  - RPD  (requests per day)      e.g. Gemini Free Tier: 1500 RPD
  - TPM  (tokens per minute)     approximate guard

If a limit would be exceeded the call is retried with exponential back-off,
then raises RateLimitExceeded so the API router returns a clean 429.

Usage:
    from backend.core.rate_limiter import gemini_rate_limiter, RateLimitExceeded
    with gemini_rate_limiter.acquire(estimated_tokens=len(prompt)//4):
        response = client.models.generate_content(...)
"""

import os
import threading
import time
import math
import logging
from collections import deque
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when all retry attempts are exhausted waiting for a rate-limit slot."""
    def __init__(self, message: str, retry_after_seconds: float = 60.0):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class SlidingWindowRateLimiter:
    """
    Thread-safe sliding-window rate limiter for the Gemini API.

    Parameters
    ----------
    rpm : int
        Maximum requests per 60-second sliding window.
    rpd : int
        Maximum requests per 86400-second (24 h) sliding window.
    tpm : int
        Maximum estimated tokens per 60-second window (0 = disabled).
    max_retries : int
        Retry attempts before raising RateLimitExceeded.
    base_backoff : float
        Initial back-off seconds; doubles on each retry.
    """

    def __init__(
        self,
        rpm: int = 15,
        rpd: int = 1_500,
        tpm: int = 1_000_000,
        max_retries: int = 5,
        base_backoff: float = 2.0,
    ):
        self.rpm = rpm
        self.rpd = rpd
        self.tpm = tpm
        self.max_retries = max_retries
        self.base_backoff = base_backoff

        self._minute_window: deque = deque()    # timestamps in last 60s
        self._day_window: deque = deque()        # timestamps in last 86400s
        self._token_window: deque = deque()      # (timestamp, token_count)
        self._lock = threading.Lock()

    def _evict_old(self, now: float) -> None:
        minute_cutoff = now - 60.0
        day_cutoff = now - 86_400.0
        while self._minute_window and self._minute_window[0] < minute_cutoff:
            self._minute_window.popleft()
        while self._day_window and self._day_window[0] < day_cutoff:
            self._day_window.popleft()
        while self._token_window and self._token_window[0][0] < minute_cutoff:
            self._token_window.popleft()

    def _tokens_in_window(self) -> int:
        return sum(t for _, t in self._token_window)

    def _seconds_until_slot(self, now: float, estimated_tokens: int) -> float:
        """Returns seconds to wait, or 0.0 if a slot is immediately available."""
        self._evict_old(now)

        if len(self._minute_window) >= self.rpm:
            wait = 60.0 - (now - self._minute_window[0]) + 0.1
            return max(wait, 0.1)

        if len(self._day_window) >= self.rpd:
            wait = 86_400.0 - (now - self._day_window[0]) + 1.0
            return max(wait, 1.0)

        if self.tpm > 0 and estimated_tokens > 0:
            current_tokens = self._tokens_in_window()
            if current_tokens + estimated_tokens > self.tpm:
                if self._token_window:
                    wait = 60.0 - (now - self._token_window[0][0]) + 0.1
                    return max(wait, 0.1)

        return 0.0

    def _record(self, now: float, estimated_tokens: int) -> None:
        self._minute_window.append(now)
        self._day_window.append(now)
        if self.tpm > 0 and estimated_tokens > 0:
            self._token_window.append((now, estimated_tokens))

    @contextmanager
    def acquire(self, estimated_tokens: int = 0):
        """
        Context manager that blocks until a Gemini API call slot is available.
        Raises RateLimitExceeded if all retries are exhausted.

        Parameters
        ----------
        estimated_tokens : int
            Rough token count for the call. Use 0 to skip TPM enforcement.
        """
        attempt = 0
        wait = 0.0
        while True:
            with self._lock:
                now = time.monotonic()
                wait = self._seconds_until_slot(now, estimated_tokens)
                if wait <= 0:
                    self._record(now, estimated_tokens)
                    break

            if attempt >= self.max_retries:
                raise RateLimitExceeded(
                    f"Gemini API rate limit reached after {self.max_retries} retries. "
                    f"Please wait ~{math.ceil(wait)}s and try again.",
                    retry_after_seconds=wait,
                )

            backoff = min(self.base_backoff * (2 ** attempt), wait)
            logger.warning(
                "[rate_limiter] Gemini slot not available - waiting %.1fs (attempt %d/%d)",
                backoff, attempt + 1, self.max_retries,
            )
            time.sleep(backoff)
            attempt += 1

        try:
            yield
        except Exception:
            raise

    def status(self) -> dict:
        """Return current usage counts (useful for debug/health endpoints)."""
        with self._lock:
            now = time.monotonic()
            self._evict_old(now)
            return {
                "requests_last_minute": len(self._minute_window),
                "requests_last_day": len(self._day_window),
                "tokens_last_minute": self._tokens_in_window(),
                "rpm_limit": self.rpm,
                "rpd_limit": self.rpd,
                "tpm_limit": self.tpm,
            }


# ---------------------------------------------------------------------------
# Singleton shared across all workers in the same process.
# Gemini 2.0 Flash free-tier defaults: 15 RPM | 1,500 RPD | 1,000,000 TPM
# Override by setting env vars before startup.
# ---------------------------------------------------------------------------
gemini_rate_limiter = SlidingWindowRateLimiter(
    rpm=int(os.getenv("GEMINI_RPM", "15")),
    rpd=int(os.getenv("GEMINI_RPD", "1500")),
    tpm=int(os.getenv("GEMINI_TPM", "1000000")),
    max_retries=int(os.getenv("GEMINI_RATE_MAX_RETRIES", "5")),
    base_backoff=float(os.getenv("GEMINI_RATE_BASE_BACKOFF", "2.0")),
)
