from unittest.mock import patch

import pytest

from src.agents.brightpath_agent import build_brightpath_agent
from src.agents.graph import GraphAgent
from src.agents.mock_llm import LLMResponse, MockLLM


QUESTION = "What is the leave policy?"


def test_pii_check_blocks_pii():
    seen = []

    def router(messages, tools):
        seen.extend(m["content"] for m in messages if m["role"] == "user")
        return LLMResponse.final("Done")

    base = build_brightpath_agent(MockLLM(router=router), memory_on=False)
    GraphAgent(base).run(f"{QUESTION} Contact alice@example.com.")

    assert len(seen) == 1
    assert "alice@example.com" not in seen[0]
    assert "leave policy" in seen[0].lower()


@pytest.mark.parametrize("budget", [0, 1])
def test_cost_limit_routes_to_degradation(budget):
    llm = MockLLM(script=[LLMResponse.tool("lookup_policy", question=QUESTION)])
    base = build_brightpath_agent(llm, memory_on=False)

    with patch.object(llm, "complete", wraps=llm.complete) as model, \
         patch.object(base, "_execute") as tool:
        result = GraphAgent(base, budget_units=budget).run(QUESTION)

    assert result.stop_reason == "cost_limit"
    assert result.answer.strip()
    assert model.call_count == budget
    tool.assert_not_called()


def test_three_units_allow_model_tool_and_final_answer():
    llm = MockLLM(script=[
        LLMResponse.tool("lookup_policy", question=QUESTION),
        LLMResponse.final("Eligible employees receive 20 days [1]."),
    ])
    base = build_brightpath_agent(llm, memory_on=False)
    response = {
        "answer": "Eligible employees receive 20 days [1].",
        "citations": [{"source": "HR_02_Annual_Leave_Policy.txt"}],
        "kb_version": "v2.w10",
    }

    with patch("src.agents.brightpath_agent.lookup_policy",
               return_value=response) as lookup:
        result = GraphAgent(base, budget_units=3).run(QUESTION)

    lookup.assert_called_once_with(question=QUESTION)
    assert result.stop_reason == "final"
    assert [step.status for step in result.steps] == ["ok"]
    assert result.answer == "Eligible employees receive 20 days [1]."