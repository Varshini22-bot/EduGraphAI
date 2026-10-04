"""
rate_limiter.py

Lightweight, in-memory sliding-window rate limiter for FastAPI authentication routes.
Requires zero external dependencies (no Redis, no third-party libraries).
Thread-safe using threading.Lock.
"""

import time
import threading
from collections import deque
from typing import Dict
from fastapi import Request, HTTPException, status


def get_client_ip(request: Request) -> str:
    """
    Safely resolves the client IP address from proxy headers or socket connection.
    Handles comma-separated X-Forwarded-For chains from reverse proxies (Render, Vercel, Cloudflare).
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # First IP in the list represents the initial client
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip

    real_ip = request.headers.get("x-real-ip")
    if real_ip and real_ip.strip():
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


class InMemoryRateLimiter:
    """
    Sliding-window in-memory rate limiter implemented as a FastAPI dependency.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60, name: str = "default"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        self._history: Dict[str, deque] = {}
        self._lock = threading.Lock()

    def __call__(self, request: Request) -> None:
        client_ip = get_client_ip(request)
        key = f"{self.name}:{client_ip}"
        now = time.monotonic()

        with self._lock:
            # Get or create timestamp deque for this key
            timestamps = self._history.setdefault(key, deque())

            # Expire timestamps outside the sliding window
            cutoff = now - self.window_seconds
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            # Check if limit exceeded
            if len(timestamps) >= self.max_requests:
                oldest = timestamps[0]
                retry_after = max(1, int(oldest + self.window_seconds - now) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please wait a moment before trying again.",
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)

    def reset(self) -> None:
        """Clears all stored rate limit history (useful for testing)."""
        with self._lock:
            self._history.clear()


# Pre-configured instances for authentication routes (5 requests per 60 seconds per IP)
login_rate_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60, name="login")
register_rate_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60, name="register")
