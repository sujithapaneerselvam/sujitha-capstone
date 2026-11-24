"""src/agents/memory.py — state-based memory for the agent.

The W15 default: a small, explicit **state** the agent remembers about a user
across sessions — a Pydantic model, saved to SQLite. This is the right pattern for
the large majority of capstones (known, structured facts like a preferred output format). Vector
and summary memory are more powerful and more complex; see docs/memory_taxonomy.md.

Two kinds of memory live here:
  - short-term — the conversation history itself (handled by the agent loop, not stored)
  - long-term  — this UserState, persisted across sessions

Forgetting is deliberate: **TTL** drops stale facts (the sane default), and the user
can explicitly forget a fact. Contradiction resolution uses last-write-wins — for a mutable
preference, a newer write replaces the old (the user is authoritative about their
own preferences). It is one strategy of several (merge, or keep versioned history);
scoped to mutable preference facts here, not a universal rule.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, Field

DEFAULT_DB = Path("data/capstone_side.db")   # notebook: local file (built in setup)
_today: Callable[[], date] = date.today


class MemoryFact(BaseModel):
    value: str
    last_updated: str          # ISO date, e.g. "2026-01-15"


class UserState(BaseModel):
    """What the agent remembers about one user. `facts` maps a key
    (e.g. 'preferred_format') to a value + when it was last set."""
    user_id: str
    facts: dict[str, MemoryFact] = Field(default_factory=dict)

    # ── updates (last-write-wins for a mutable pref → contradiction resolution) ──
    def set(self, key: str, value: str, today: Callable[[], date] = _today) -> None:
        self.facts[key] = MemoryFact(value=value, last_updated=today().isoformat())

    def get(self, key: str) -> str | None:
        f = self.facts.get(key)
        return f.value if f else None

    def forget(self, key: str) -> bool:
        """User-controlled forgetting — an explicit 'forget X'."""
        return self.facts.pop(key, None) is not None

    # ── forgetting strategy: TTL ────────────────────────────────────────────
    def apply_ttl(self, days: int = 30, today: Callable[[], date] = _today) -> list[str]:
        """Drop facts whose last_updated is older than `days`. Returns dropped keys."""
        cutoff = today() - timedelta(days=days)
        dropped = [k for k, f in self.facts.items()
                   if date.fromisoformat(f.last_updated) < cutoff]
        for k in dropped:
            del self.facts[k]
        return dropped

    # ── render for the system prompt (short + relevant only) ────────────────
    def to_prompt(self) -> str:
        if not self.facts:
            return ""
        lines = [f"- {k.replace('_', ' ')}: {f.value}" for k, f in sorted(self.facts.items())]
        return "What you remember about this user:\n" + "\n".join(lines)


class MemoryStore:
    """SQLite-backed persistence for UserState. One row per (user_id, key)."""

    def __init__(self, db_path: Path | str = DEFAULT_DB):
        self.db_path = Path(db_path)
        self._ensure_table()

    def _ensure_table(self) -> None:
        con = sqlite3.connect(self.db_path)
        con.execute("""CREATE TABLE IF NOT EXISTS user_memory (
            user_id TEXT NOT NULL, key TEXT NOT NULL,
            value TEXT NOT NULL, last_updated TEXT NOT NULL,
            PRIMARY KEY (user_id, key))""")
        con.commit(); con.close()

    def load_state(self, user_id: str) -> UserState:
        con = sqlite3.connect(self.db_path)
        rows = con.execute("SELECT key, value, last_updated FROM user_memory WHERE user_id=?",
                           (user_id,)).fetchall()
        con.close()
        facts = {k: MemoryFact(value=v, last_updated=lu) for k, v, lu in rows}
        return UserState(user_id=user_id, facts=facts)

    def save_state(self, state: UserState) -> None:
        con = sqlite3.connect(self.db_path)
        con.execute("DELETE FROM user_memory WHERE user_id=?", (state.user_id,))
        con.executemany(
            "INSERT INTO user_memory (user_id, key, value, last_updated) VALUES (?,?,?,?)",
            [(state.user_id, k, f.value, f.last_updated) for k, f in state.facts.items()])
        con.commit(); con.close()

    def clear(self, user_id: str) -> None:
        con = sqlite3.connect(self.db_path)
        con.execute("DELETE FROM user_memory WHERE user_id=?", (user_id,))
        con.commit(); con.close()


# ─── the two hooks the agent loop uses ──────────────────────────────────────
def load_for_prompt(store: MemoryStore, user_id: str, ttl_days: int = 30,
                    today: Callable[[], date] = _today) -> tuple[UserState, str]:
    """Load state, apply TTL, and render it for the system prompt.
    Returns (state, prompt_block). Called at the START of a run when memory is on."""
    state = store.load_state(user_id)
    dropped = state.apply_ttl(days=ttl_days, today=today)
    if dropped:
        store.save_state(state)          # persist the forgetting
    return state, state.to_prompt()


def update_from_turn(store: MemoryStore, state: UserState, question: str,
                     today: Callable[[], date] = _today) -> str | None:
    """User-controlled memory: honour explicit 'remember …' / 'forget …' in the
    user's message. Called at the END of a run when memory is on. Returns a note."""
    q = question.strip()
    low = q.lower()
    if low.startswith("remember that "):
        payload = q[len("remember that "):].strip().rstrip(".")
        if " is " in payload:
            key, value = payload.split(" is ", 1)
            state.set(key.strip().replace(" ", "_"), value.strip(), today=today)
            store.save_state(state)
            return f"remembered {key.strip()} = {value.strip()}"
    if low.startswith("forget "):
        key = low[len("forget "):].strip().rstrip(".").replace(" ", "_")
        if state.forget(key):
            store.save_state(state)
            return f"forgot {key}"
    return None
