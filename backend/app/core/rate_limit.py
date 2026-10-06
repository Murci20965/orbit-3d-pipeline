"""In-process request limits for a single-instance deployment.

The engine runs as one uvicorn process on a Hugging Face Space, so plain
in-memory counters are enough. Two layers, because they protect against
different things:

- A GLOBAL cap per time window. This is the real protection for paid API
  credits: it does not depend on who the caller claims to be.
- A best-effort PER-CLIENT cap, keyed on the address the platform proxy
  appended to X-Forwarded-For. A caller can forge earlier entries in that
  header, so this layer only slows casual abuse; the global cap bounds spend.

CORS does not help here: it only stops other websites' browsers, never
curl or scripts.
"""

import threading
import time
from collections import deque
from typing import Callable, Deque, Dict

_SWEEP_EVERY = 500  # calls between sweeps of idle keys (bounds memory)


class SlidingWindowLimiter:
    """Allow at most `limit` events per `window_s` seconds for each key."""

    def __init__(self, limit: int, window_s: float, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window_s = window_s
        self._clock = clock
        self._hits: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()
        self._calls = 0

    def allow(self, key: str) -> bool:
        now = self._clock()
        with self._lock:
            self._calls += 1
            if self._calls % _SWEEP_EVERY == 0:
                self._sweep(now)
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] >= self.window_s:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True

    def _sweep(self, now: float) -> None:
        stale = [k for k, q in self._hits.items() if not q or now - q[-1] >= self.window_s]
        for k in stale:
            del self._hits[k]


def client_key(request) -> str:
    """The client address as the platform proxy saw it (last X-Forwarded-For hop)."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"
