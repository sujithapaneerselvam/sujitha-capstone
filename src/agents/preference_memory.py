"""Restricted memory for BrightPath response-format preferences."""
from src.agents.memory import MemoryStore, load_for_prompt

KEY = "preferred_format"
ALLOWED_VALUES = {"bullets", "prose"}


def remember_format(
    store: MemoryStore, user_id: str, value: str
) -> None:
    if value not in ALLOWED_VALUES:
        raise ValueError("Format must be 'bullets' or 'prose'")

    state = store.load_state(user_id)
    state.set(KEY, value)
    store.save_state(state)


def forget_format(store: MemoryStore, user_id: str) -> None:
    state = store.load_state(user_id)
    state.forget(KEY)
    store.save_state(state)


def format_for_prompt(
    store: MemoryStore, user_id: str, ttl_days: int = 30
) -> str:
    state, _ = load_for_prompt(store, user_id, ttl_days=ttl_days)
    value = state.get(KEY)

    if value not in ALLOWED_VALUES:
        return ""

    return (
        f"The user prefers {value} formatting. "
        "Apply this preference only to presentation. "
        "Retrieve current policy facts and preserve source citations."
    )