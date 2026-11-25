"""LangGraph port of the BrightPath raw agent.

PII and cost guardrails will be added after baseline parity checks.
"""
from __future__ import annotations

import json
import operator
from typing import Annotated, TypedDict
from src.ingest.pipeline import _scrub_text as scrub_pii
from langgraph.graph import StateGraph, START, END

from src.agents.raw_react import (
    AgentResult,
    Step,
    SYSTEM,
    load_for_prompt,
    update_from_turn,
)


class GraphState(TypedDict):
    question: str
    messages: list[dict]
    steps: Annotated[list[dict], operator.add]
    answer: str
    iterations: int
    pending: dict | None
    finished: bool
    stop_reason: str
    memory_used: bool
    prompt_chars: int
    remaining_units: int


class GraphAgent:
    """Wrap an existing BrightPath agent without replacing its defenses."""

    def __init__(self, base_agent, *, budget_units=None):
        self.base = base_agent
        # Allow one model call and one tool call per iteration by default.
        self.budget_units = (
            2 * base_agent.max_iter if budget_units is None else budget_units
        )
        if not isinstance(self.budget_units, int) or self.budget_units < 0:
            raise ValueError("budget_units must be a non-negative integer")
        
        graph = StateGraph(GraphState)
        graph.add_node("think", self._think)
        graph.add_node("tool", self._tool)
        graph.add_node("iteration_limit", self._iteration_limit)
        graph.add_node("pii_check", self._pii_check)
        graph.add_node("cost_limit", self._cost_limit)

        graph.add_edge(START, "pii_check")
        graph.add_edge("pii_check", "cost_limit")
        graph.add_conditional_edges(
            "cost_limit",
            self._after_cost_check,
            {"done": END, "think": "think", "tool": "tool"},
        )
        graph.add_conditional_edges(
            "think",
            lambda s: "done" if s["finished"] else "check",
            {"done": END, "check": "cost_limit"},
        )
        graph.add_conditional_edges(
            "tool",
            lambda s: "limit" if s["iterations"] >= self.base.max_iter else "check",
            {"limit": "iteration_limit", "check": "cost_limit"},
        )
        graph.add_edge("iteration_limit", END)

        self.app = graph.compile()

    def _cost_limit(self, state):
        # Reserve one simulated unit for the next model or tool call.
        if state["remaining_units"] == 0:
            return {
                "finished": True,
                "pending": None,
                "stop_reason": "cost_limit",
                "answer": "I stopped before the next call because the request budget was exhausted.",
            }
        return {"remaining_units": state["remaining_units"] - 1}

    def _after_cost_check(self, state):
        if state["finished"]:
            return "done"
        return "tool" if state["pending"] is not None else "think"
    def _think(self, state):
        response = self.base.llm.complete(
            state["messages"], self.base.tools
        )
        updates = {
            "iterations": state["iterations"] + 1,
            "prompt_chars": state["prompt_chars"] + sum(
                len(str(message.get("content") or ""))
                for message in state["messages"]
            ),
        }

        if response.kind == "final":
            updates.update(
                answer=response.content or "",
                finished=True,
                pending=None,
            )
        else:
            updates.update(
                finished=False,
                pending={
                    "name": response.tool_name,
                    "args": response.tool_args or {},
                },
            )
        return updates

    def _tool(self, state):
        call = state["pending"]
        name, args = call["name"], call["args"]

        # Reuses raw agent validation and DefensePolicy.guard().
        observation, status = self.base._execute(name, args)

        call_id = f"call_{state['iterations']}"
        messages = state["messages"] + [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args),
                    },
                }],
            },
            {
                "role": "tool",
                "tool_call_id": call_id,
                "content": observation,
            },
        ]

        return {
            "messages": messages,
            "steps": [{
                "tool": name,
                "args": args,
                "observation": observation,
                "status": status,
            }],
            "pending": None,
        }

    def _iteration_limit(self, state):
        return {
            "answer": (
                "(stopped after the maximum number of steps — "
                "I couldn't reach a final answer safely.)"
            ),
            "finished": True,
            "stop_reason": "max_iter",
        }

    def run(self, question):
        system = SYSTEM
        memory_state = None
        memory_used = False
        kwargs = {}

        if self.base.today is not None:
            kwargs["today"] = self.base.today

        if self.base.memory is not None:
            memory_state, block = load_for_prompt(
                self.base.memory,
                self.base.user_id,
                ttl_days=self.base.ttl_days,
                **kwargs,
            )
            if block:
                system += "\n\n" + block
                memory_used = True

        output = self.app.invoke(
            {
                "question": question,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": question},
                ],
                "steps": [],
                "answer": "",
                "iterations": 0,
                "pending": None,
                "finished": False,
                "stop_reason": "final",
                "memory_used": memory_used,
                "prompt_chars": 0,
                "remaining_units": self.budget_units,
            },
            # Graph supersteps are not the same as LLM iterations.
            config={"recursion_limit": 4 * self.base.max_iter + 5},
        )

        note = None
        if memory_state is not None:
            note = update_from_turn(
                self.base.memory,
                memory_state,
                question,
                **kwargs,
            )

        return AgentResult(
            question=question,
            answer=output["answer"],
            steps=[Step(**step) for step in output["steps"]],
            iterations=output["iterations"],
            stop_reason=output["stop_reason"],
            memory_used=output["memory_used"],
            memory_note=note,
            prompt_chars=output["prompt_chars"],
        )

    def _pii_check(self, state):
        clean, flags = scrub_pii(state["question"])

        messages = [
            {**message, "content": clean}
            if message["role"] == "user"
            else message
            for message in state["messages"]
        ]

        return {"question": clean, "messages": messages}