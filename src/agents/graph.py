"""LangGraph port of the BrightPath raw agent.

PII and cost guardrails will be added after baseline parity checks.
"""
from __future__ import annotations

import json
import re
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
    plan: list[dict]
    plan_index: int
    retried: bool
    evidence: list[str]
    reflection_retries: int


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
        graph.add_node("pii_check", self._pii_check)
        graph.add_node("think", self._think)
        graph.add_node("tool", self._tool)
        graph.add_node("iteration_limit", self._iteration_limit)
        graph.add_node("cost_limit", self._cost_limit)

        graph.add_edge(START, "pii_check")
        graph.add_node("plan", self._plan)
        graph.add_node("reflect", self._reflect)

        graph.add_conditional_edges(
            "pii_check",
            self._route_question,
            {"plan": "plan", "simple": "cost_limit"},
        )
        graph.add_edge("plan", "cost_limit")
       
        
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
            lambda s: (
                "reflect" if s["plan"]
                else "limit" if s["iterations"] >= self.base.max_iter
                else "check"
            ),
            {
                "reflect": "reflect",
                "limit": "iteration_limit",
                "check": "cost_limit",
            },
        )
        graph.add_conditional_edges(
            "reflect",
            lambda s: (
                "done" if s["finished"]
                else "limit" if s["iterations"] >= self.base.max_iter
                else "check"
            ),
            {"done": END, "limit": "iteration_limit", "check": "cost_limit"},
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
    
    def _route_question(self, state):
        q = state["question"].lower()
        asks_leave = "leave" in q
        asks_entitlement = any(
            term in q for term in ("entitlement", "how many days", "allowance")
        )
        asks_notice = any(
            term in q for term in ("notice", "advance", "how early")
        )
        return "plan" if asks_leave and asks_entitlement and asks_notice else "simple"

    def _plan(self, state):
        # Preserve the redacted original question, including any conditions.
        q = state["question"]
        plan = [
            {
                "label": "Annual-leave entitlement",
                "query": f"{q}\nAnswer only the entitlement part. Cite the policy.",
                "retry": "Find the annual entitlement clause and its number of days.",
            },
            {
                "label": "Advance notice",
                "query": f"{q}\nAnswer only the advance-notice part. Cite the policy.",
                "retry": "Find the request deadline for the leave duration in the question.",
            },
        ]
        return {
            "plan": plan,
            "pending": {
                "name": "lookup_policy",
                "args": {"question": plan[0]["query"]},
            },
        }

    def _reflect(self, state):
        i = state["plan_index"]
        item = state["plan"][i]
        step = state["steps"][-1]

        try:
            payload = json.loads(step["observation"])
        except (TypeError, ValueError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

        answer = str(payload.get("answer") or "").strip()
        citations = payload.get("citations") or []
        sources = list(dict.fromkeys(
            c["source"] for c in citations
            if isinstance(c, dict) and isinstance(c.get("source"), str)
            and c["source"].strip()
        ))

        # A successful HTTP call alone does not establish evidence.
        # These checks apply only to this two-part leave-policy exercise.
        day_count = re.search(
            r"\b(?:\d+|one|two|three|five|ten|twenty)\s+"
            r"(?:(?:working|business|calendar)\s+)?days?\b", answer, re.I
        )
        topic = (
            re.search(r"\b(annual|year|yearly)\b", answer, re.I)
            if i == 0 else
            re.search(r"\b(advance|notice|before|prior)\b", answer, re.I)
        )
        abstained = re.search(
            r"cannot verify|could not verify|does not specify|"
            r"not enough information|insufficient|don't know", answer, re.I
        )
        supported = bool(
            step["status"] == "ok" and sources and day_count and topic and not abstained
        )

        if not supported and not state["retried"]:
            return {
                "retried": True,
                "reflection_retries": state["reflection_retries"] + 1,
                "pending": {
                    "name": "lookup_policy",
                    "args": {"question": item["query"] + "\n" + item["retry"]},
                },
            }

        detail = (
            f"{answer} (Source: {', '.join(sources)})"
            if supported else "Could not verify this part from the policy evidence."
        )
        evidence = state["evidence"] + [f"{item['label']}: {detail}"]
        next_i = i + 1

        if next_i == len(state["plan"]):
            return {
                "evidence": evidence,
                "answer": "\n".join("- " + line for line in evidence),
                "finished": True,
                "pending": None,
                "stop_reason": "final",
            }

        return {
            "evidence": evidence,
            "plan_index": next_i,
            "retried": False,
            "pending": {
                "name": "lookup_policy",
                "args": {"question": state["plan"][next_i]["query"]},
            },
        }

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
                "plan": [],
                "plan_index": 0,
                "retried": False,
                "evidence": [],
                "reflection_retries": 0,
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