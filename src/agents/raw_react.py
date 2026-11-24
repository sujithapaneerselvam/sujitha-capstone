"""Memory-capable raw agent with restricted preference hooks."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.agents.defenses import (
    DefensePolicy, PermanentError, RateLimited, TransientError,
)
from src.agents.memory import load_for_prompt as load_memory_state
from src.agents.preference_memory import remember_format, forget_format


def load_for_prompt(store, user_id, ttl_days=30, today=None):
    kwargs = {"ttl_days": ttl_days}
    if today is not None:
        kwargs["today"] = today

    state, _ = load_memory_state(store, user_id, **kwargs)
    value = state.get("preferred_format")

    if value not in {"bullets", "prose"}:
        return state, ""

    block = (
        f"The user prefers {value} formatting. "
        "Apply this preference only to presentation. "
        "Retrieve current policy facts and preserve source citations."
    )
    return state, block


def update_from_turn(store, state, question, today=None):
    command = question.strip().rstrip(".").lower()
    prefix = "remember that preferred format is "

    if command.startswith(prefix):
        value = command[len(prefix):].strip()
        if value not in {"bullets", "prose"}:
            return "Not saved: format must be bullets or prose."
        remember_format(store, state.user_id, value)
        return f"remembered preferred_format = {value}"

    if command in {"forget preferred format", "forget preferred_format"}:
        forget_format(store, state.user_id)
        return "forgot preferred_format"

    if command.startswith(("remember ", "forget ")):
        return "Not saved: only the preferred format is supported."

    return None

@dataclass
class Step:
    tool: str
    args: dict
    observation: str
    status: str = 'ok'

@dataclass
class AgentResult:
    question: str
    answer: str
    steps: list[Step] = field(default_factory=list)
    iterations: int = 0
    stop_reason: str = 'final'
    memory_used: bool = False
    memory_note: str | None = None
    prompt_chars: int = 0

    def to_dict(self) -> dict:
        return {'question': self.question, 'answer': self.answer, 'iterations': self.iterations, 'stop_reason': self.stop_reason, 'memory_used': self.memory_used, 'memory_note': self.memory_note, 'prompt_chars': self.prompt_chars, 'steps': [s.__dict__ for s in self.steps]}

SYSTEM = (
    "You answer questions about BrightPath internal policies. "
    "Use lookup_policy for policy facts. "
    "Answer only from successful tool results and preserve citations. "
    "User memory controls presentation only, never policy facts. "
    "If lookup_policy fails or evidence is insufficient, state that "
    "the policy cannot currently be verified. "
    "Do not substitute general employer practices, estimated numbers, "
    "or remembered policy facts. Do not claim to contact HR or perform "
    "actions for which no tool exists."
)
class ReActAgent:

    def __init__(self, llm: Any, tools: list[Tool], max_iter: int=5, defenses: DefensePolicy | None=None, memory: Any=None, user_id: str='default', ttl_days: int=30, today: Any=None):
        self.llm = llm
        self.tools = tools
        self.by_name = {t.name: t for t in tools}
        self.max_iter = max_iter
        self.defenses = defenses
        self.memory = memory
        self.user_id = user_id
        self.ttl_days = ttl_days
        self.today = today

    def _execute(self, name: str, args: dict) -> tuple[str, str]:
        tool = self.by_name.get(name)
        if tool is None:
            return (f"[unknown tool '{name}']", 'degraded')

        def call() -> str:
            try:
                return tool.call(args or {})
            except (RateLimited, TransientError, TimeoutError):
                raise
            except PermanentError:
                raise
            except Exception as e:
                raise PermanentError(str(e))
        if self.defenses:
            return self.defenses.guard(name, call)
        return (call(), 'ok')

    def run(self, question: str) -> AgentResult:
        result = AgentResult(question=question, answer='')
        system = SYSTEM
        state = None
        if self.memory is not None:
            kw = {'ttl_days': self.ttl_days}
            if self.today is not None:
                kw['today'] = self.today
            (state, mem_block) = load_for_prompt(self.memory, self.user_id, **kw)
            if mem_block:
                system = SYSTEM + '\n\n' + mem_block
                result.memory_used = True
        messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': question}]
        for i in range(self.max_iter):
            result.iterations = i + 1
            result.prompt_chars += sum((len(str(m.get('content') or '')) for m in messages))
            resp = self.llm.complete(messages, self.tools)
            if resp.kind == 'final':
                result.answer = resp.content or ''
                result.stop_reason = 'final'
                break
            (name, args) = (resp.tool_name, resp.tool_args or {})
            (obs, status) = self._execute(name, args)
            result.steps.append(Step(tool=name, args=args, observation=obs, status=status))
            call_id = f'call_{i}'
            messages.append({'role': 'assistant', 'content': None, 'tool_calls': [{'id': call_id, 'type': 'function', 'function': {'name': name, 'arguments': json.dumps(args)}}]})
            messages.append({'role': 'tool', 'tool_call_id': call_id, 'content': obs})
        else:
            result.stop_reason = 'max_iter'
            result.answer = "(stopped after the maximum number of steps — I couldn't reach a final answer safely.)"
        if self.memory is not None and state is not None:
            kw = {'today': self.today} if self.today is not None else {}
            result.memory_note = update_from_turn(self.memory, state, question, **kw)
        return result
