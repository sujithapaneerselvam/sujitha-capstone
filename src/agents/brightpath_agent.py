"""BrightPath policy tool and memory-capable agent factory."""
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

from src.agents.defenses import (
    DefensePolicy, PermanentError, TransientError,
)
from src.agents.memory import MemoryStore
from src.agents.raw_react import ReActAgent
from src.agents.tool_base import Tool
from src.rag.policy_tool import (
    LookupPolicyInput, TOOL_DESCRIPTION, lookup_policy,
)


class LookupPolicyTool(Tool):
    name = "lookup_policy"
    description = TOOL_DESCRIPTION
    Args = LookupPolicyInput
    idempotent = True
    has_side_effects = False

    def run(self, question: str) -> str:
        try:
            result = lookup_policy(question=question)
        except HTTPError as error:
            if error.code in {408, 429, 500, 502, 503, 504}:
                raise TransientError(str(error)) from error
            raise PermanentError(str(error)) from error
        except (URLError, TimeoutError) as error:
            raise TransientError(str(error)) from error
        except RuntimeError as error:
            raise PermanentError(str(error)) from error

        return json.dumps(result, ensure_ascii=False)


def build_brightpath_agent(
    llm,
    *,
    memory_on=False,
    user_id="demo-user",
    db_path="data/brightpath_memory.db",
):
    store = None
    if memory_on:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        store = MemoryStore(path)

    policy = DefensePolicy(
        breaker_tools=("lookup_policy",),
        write_tools=(),
        retries=3,
        fail_max=3,
    )

    return ReActAgent(
        llm=llm,
        tools=[LookupPolicyTool()],
        defenses=policy,
        memory=store,
        user_id=user_id,
        ttl_days=30,
        max_iter=5,
    )