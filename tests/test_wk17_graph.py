from src.agents.brightpath_agent import build_brightpath_agent
from src.agents.graph import GraphAgent
from src.agents.mock_llm import MockLLM
from unittest.mock import patch

import pytest

def test_leave_question_routing_and_plan():
    base = build_brightpath_agent(MockLLM(script=[]), memory_on=False)
    agent = GraphAgent(base)

    simple = {"question": "How many days of annual leave do I receive?"}
    assert agent._route_question(simple) == "simple"

    question = (
        "How many days of annual leave do I receive for a complete calendar "
        "year, and how much advance notice must I give for three consecutive days?"
    )
    state = {"question": question}
    assert agent._route_question(state) == "plan"

    plan = agent._plan(state)["plan"]
    assert len(plan) == 2
    assert "entitlement" in plan[0]["label"].lower()
    assert "notice" in plan[1]["label"].lower()
    assert all(question in item["query"] for item in plan)


@pytest.mark.parametrize(
    "retry_succeeds",
    [True, False],
    ids=["retry-recovers", "retry-exhausted"],
)
def test_planned_lookup_reflects_and_finishes(retry_succeeds):
    source = "HR_02_Annual_Leave_Policy.txt"
    question = (
        "How many days of annual leave do I receive for a complete calendar "
        "year, and how much advance notice must I give for three consecutive days?"
    )

    def reply(answer, cited=True):
        return {
            "answer": answer,
            "citations": [{"source": source}] if cited else [],
            "kb_version": "v2.w10",
        }

    # The first answer sounds correct but has no citation.
    # Reflection should retry even though the tool returned normally.
    unsupported = reply("Annual leave is 20 days per year.", cited=False)
    entitlement = reply("Annual leave is 20 days per year.")
    notice = reply("Submit the request at least 10 working days in advance.")

    base = build_brightpath_agent(MockLLM(script=[]), memory_on=False)
    agent = GraphAgent(base, budget_units=6)

    with patch(
        "src.agents.brightpath_agent.lookup_policy",
        side_effect=[
            unsupported,
            entitlement if retry_succeeds else unsupported,
            notice,
        ],
    ) as lookup:
        result = agent.run(question)

    # Exactly one retry for entitlement, then a lookup for notice.
    assert lookup.call_count == 3
    queries = [call.kwargs["question"] for call in lookup.call_args_list]
    assert "entitlement" in queries[0].lower()
    assert queries[1].startswith(queries[0] + "\n")
    assert "advance-notice" in queries[2].lower()

    assert result.stop_reason == "final"
    parts = result.answer.splitlines()
    assert len(parts) == 2
    assert "Annual-leave entitlement:" in parts[0]
    assert "Advance notice:" in parts[1]
    assert "10 working days" in parts[1] and source in parts[1]

    if retry_succeeds:
        assert "20 days" in parts[0] and source in parts[0]
    else:
        assert "Could not verify this part" in parts[0]
        assert "20 days" not in parts[0]
        assert source not in parts[0]