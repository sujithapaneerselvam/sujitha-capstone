"""src/agents/mock_llm.py — the LLM behind the agent, and how we mock it.

The single most useful testing skill this week is **mocking the LLM**. A real LLM
call is slow, costs money, and is non-deterministic — useless in a test. So the
agent talks to a tiny interface:

    llm.complete(messages, tools) -> LLMResponse   # either a tool call or a final answer

Two implementations:
  MockLLM  — deterministic and offline. Give it a *script* (a fixed list of
             responses, for tests) or let it keyword-route one tool call then a
             final answer (for offline runs). No network, no key, milliseconds.
  OpenAILLM — the real thing (OpenAI function calling). Needs OPENAI_API_KEY.

Everything in this package runs on MockLLM, which is why the whole thing — agent,
defenses, the five failure scenarios, the test suite — works with no credentials.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable

# Tool is defined in the cell above


@dataclass
class LLMResponse:
    kind: str                      # "tool_use" | "final"
    tool_name: str | None = None
    tool_args: dict | None = None
    content: str | None = None

    @staticmethod
    def tool(name: str, **args) -> "LLMResponse":
        return LLMResponse("tool_use", tool_name=name, tool_args=args)

    @staticmethod
    def final(content: str) -> "LLMResponse":
        return LLMResponse("final", content=content)


class MockLLM:
    """A deterministic stand-in for a function-calling LLM.

    - Scripted:  MockLLM(script=[LLMResponse.tool('calculate', expression='2+2'),
                                 LLMResponse.final('It is 4.')])
                 returns those in order (extra calls repeat the last one).
    - Keyword:   MockLLM()  → routes ONE tool call by keyword, then a final answer
                 synthesised from the observation. Good for offline demos.
    """

    def __init__(self, script: list[LLMResponse] | None = None,
                 router: Callable[[list[dict], list[Tool]], LLMResponse] | None = None):
        self.script = list(script) if script else None
        self.router = router
        self.calls = 0

    def complete(self, messages: list[dict], tools: list[Tool]) -> LLMResponse:
        self.calls += 1
        if self.script is not None:
            return self.script.pop(0) if self.script else LLMResponse.final(
                "(no more scripted responses)")
        if self.router is not None:
            return self.router(messages, tools)
        return self._keyword_route(messages, tools)

    # ── default keyword routing: one tool call, then a final answer ──────────
    def _keyword_route(self, messages: list[dict], tools: list[Tool]) -> LLMResponse:
        # If a tool has already produced an observation, answer from it.
        obs = _last_observation(messages)
        if obs is not None:
            return LLMResponse.final(f"Based on the tool result: {obs}")
        q = _last_user(messages).lower()
        names = {t.name for t in tools}
        if "calculate" in names and re.search(r"\d\s*[-+*/%]\s*\d|percent|%|how much is", q):
            return LLMResponse.tool("calculate", expression=_extract_expr(q))
        sql_kw = ("how many doc", "which department", "what version", "list the", "count",
                  "how many hr", "how many it", "how many finance", "updated", "chunk")
        if "query_sql" in names and any(k in q for k in sql_kw):
            return LLMResponse.tool("query_sql",
                                    sql="SELECT COUNT(*) AS total_documents FROM document_metadata",
                                    purpose="metadata question")
        web_kw = ("latest", "current", "today", "news", "price", "recent", "2026", "who won")
        if "search_web" in names and any(k in q for k in web_kw):
            return LLMResponse.tool("search_web", query=_last_user(messages), max_results=3)
        return LLMResponse.final("I can answer that directly: (no tool needed).")


# ─── real OpenAI adapter (needs a key + network) ────────────────────────────
class OpenAILLM:
    def __init__(self, model: str = "gpt-5-mini"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def complete(self, messages: list[dict], tools: list[Tool]) -> LLMResponse:
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages,
            tools=[t.openai_schema() for t in tools], tool_choice="auto")
        msg = resp.choices[0].message
        if msg.tool_calls:
            call = msg.tool_calls[0]
            return LLMResponse.tool(call.function.name, **json.loads(call.function.arguments or "{}"))
        return LLMResponse.final(msg.content or "")


# ─── tiny helpers ───────────────────────────────────────────────────────────
def _last_user(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def _last_observation(messages: list[dict]) -> str | None:
    for m in reversed(messages):
        if m.get("role") == "tool":
            return str(m.get("content", ""))
    return None


def _extract_expr(q: str) -> str:
    m = re.search(r"[0-9][0-9\.\s\+\-\*/%\(\)]*[0-9\)]", q)
    return m.group(0).strip() if m else "0"
