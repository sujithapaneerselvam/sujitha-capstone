"""src/agents/defenses.py — Failure-Oriented Design, in code.

Five failure categories, five defenses:

    Transient    (429, network blip)        → retry with backoff
    Permanent    (bad args, bad schema)     → fast-fail (do NOT retry)
    Silent       (wrong-but-valid result)   → validation / sanity checks (in the tools)
    Cascading    (timeout floods downstream)→ circuit breaker
    Adversarial  (injection, misuse)         → tool permissioning (+ sanitisation)

`DefensePolicy.guard(tool_name, call)` wraps a single tool call with permissioning,
a circuit breaker, retry-with-backoff, and graceful degradation, so one bad tool
can't crash the agent. Deterministic and offline (backoff sleeps are disabled in
tests via sleep=lambda _: None).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable


# ─── failure types ──────────────────────────────────────────────────────────
class TransientError(Exception):
    """Temporary — a retry will probably succeed (e.g. network blip)."""


class RateLimited(TransientError):
    """HTTP 429 — transient, back off and retry."""


class PermanentError(Exception):
    """Won't fix itself — retrying is harmful (bad credentials, bad schema/args)."""


def classify(exc: Exception) -> str:
    """Map an exception to a failure category (the diagnostic the week teaches)."""
    if isinstance(exc, RateLimited):
        return "transient"
    if isinstance(exc, TransientError) or isinstance(exc, TimeoutError):
        return "transient"      # timeouts retry, but repeated ones trip the breaker → cascading
    if isinstance(exc, PermanentError):
        return "permanent"
    return "permanent"          # unknown = don't blindly retry


# ─── circuit breaker (hand-rolled: CLOSED / OPEN / HALF_OPEN) ────────────────
class CircuitOpen(Exception):
    """Raised when the breaker is open and the call is short-circuited."""


class CircuitBreaker:
    """Opens after `fail_max` consecutive failures; after `reset_timeout` it moves
    to HALF_OPEN and lets one trial call through. Success closes it; failure
    re-opens it. This is the cascading-failure defense."""

    def __init__(self, fail_max: int = 3, reset_timeout: float = 30.0,
                 now: Callable[[], float] = time.monotonic):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._now = now
        self.state = "closed"
        self.failures = 0
        self.opened_at = 0.0

    def _can_attempt(self) -> bool:
        if self.state == "open":
            if self._now() - self.opened_at >= self.reset_timeout:
                self.state = "half_open"
                return True
            return False
        return True

    def record_success(self) -> None:
        self.failures = 0
        self.state = "closed"

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.fail_max:
            self.state = "open"
            self.opened_at = self._now()

    def call(self, fn: Callable[[], str]) -> str:
        if not self._can_attempt():
            raise CircuitOpen(f"circuit open (>{self.fail_max} failures)")
        try:
            result = fn()
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result


# ─── retry with exponential backoff (the transient defense) ─────────────────
def retry_with_backoff(fn: Callable[[], str], attempts: int = 3, base: float = 0.2,
                       sleep: Callable[[float], None] = time.sleep) -> str:
    """Retry on TransientError/TimeoutError with exponential backoff. PermanentError
    is re-raised immediately (fast-fail)."""
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except PermanentError:
            raise                                   # never retry a permanent failure
        except (TransientError, TimeoutError) as e:
            last = e
            if i < attempts - 1:
                sleep(base * (2 ** i))
    raise last if last else RuntimeError("retry failed")


# ─── the policy that wraps every tool call ──────────────────────────────────
@dataclass
class DefensePolicy:
    retries: int = 3
    breaker_tools: tuple[str, ...] = ("search_web", "query_sql")   # external / can time out
    write_tools: tuple[str, ...] = ("send_email",)       # gated behind confirmation
    fail_max: int = 3
    sleep: Callable[[float], None] = time.sleep
    breakers: dict = field(default_factory=dict)

    def __post_init__(self):
        for t in self.breaker_tools:
            self.breakers.setdefault(t, CircuitBreaker(fail_max=self.fail_max))

    def guard(self, tool_name: str, call: Callable[[], str]) -> tuple[str, str]:
        """Run a tool call under the defenses. Returns (observation, status) where
        status ∈ {ok, degraded, blocked}. Never raises — the agent must survive."""
        # 1 · Adversarial → tool permissioning: gate side-effecting tools.
        if tool_name in self.write_tools:
            return (f"[{tool_name} BLOCKED — requires human confirmation before a "
                    f"side-effecting action]", "blocked")

        breaker = self.breakers.get(tool_name)

        def attempt() -> str:
            return breaker.call(call) if breaker else call()

        # 2 · Cascading → if the breaker is already open, degrade fast.
        try:
            obs = retry_with_backoff(attempt, attempts=self.retries, sleep=self.sleep)
            return obs, "ok"
        except CircuitOpen as e:
            return (f"[{tool_name} unavailable — {e}; answering without it]", "degraded")
        except Exception as e:                       # transient exhausted / permanent
            cat = classify(e)
            return (f"[{tool_name} failed ({cat}: {e}); answering without it]", "degraded")
