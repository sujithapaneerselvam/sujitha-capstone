"""src/agents/tools/base.py — the Tool contract.

A tool an LLM can call reliably is four things done well (the W13 principles):
  1. a good NAME       — a verb, specific, snake_case
  2. a typed SCHEMA    — a Pydantic model: required fields, sensible defaults
  3. a DESCRIPTION     — written for the *model*, saying WHEN to use the tool
  4. IDEMPOTENCY        — declared, so the loop knows if a retry is safe

Every tool subclasses `Tool`, sets those four, and implements `run`. The same
definition exports to both OpenAI function-calling and Anthropic tool-use schemas.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Tool:
    name: str = ""
    description: str = ""
    Args: type[BaseModel] = BaseModel
    idempotent: bool = True          # is calling this twice with the same args safe?
    has_side_effects: bool = False   # does it change external state?

    def run(self, **kwargs: Any) -> str:
        raise NotImplementedError

    # ── validation + execution ────────────────────────────────────────────
    def call(self, arguments: dict[str, Any]) -> str:
        """Validate arguments against the schema, then run."""
        args = self.Args(**(arguments or {}))
        return self.run(**args.model_dump())

    # ── provider schema exports ───────────────────────────────────────────
    def parameters_schema(self) -> dict:
        return self.Args.model_json_schema()

    def openai_schema(self) -> dict:
        return {"type": "function",
                "function": {"name": self.name,
                             "description": self.description,
                             "parameters": self.parameters_schema()}}

    def anthropic_schema(self) -> dict:
        return {"name": self.name,
                "description": self.description,
                "input_schema": self.parameters_schema()}
