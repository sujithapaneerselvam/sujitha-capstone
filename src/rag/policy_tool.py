from typing import Annotated
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from pydantic import BaseModel, StringConstraints


class LookupPolicyInput(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


TOOL_NAME = "lookup_policy"
TOOL_DESCRIPTION = (
    "Use for questions about BrightPath internal policies, such as leave, "
    "remote work, benefits, and travel expenses. Returns a policy answer "
    "and source metadata. Do not use for public facts, calculations, "
    "or requests to submit claims or change records."
)
TOOL_IDEMPOTENT = True


def lookup_policy(question: str) -> dict:
    args = LookupPolicyInput(question=question)
    params = urlencode({"use_cache": "false"})
    request = Request(
        f"http://127.0.0.1:8000/ask?{params}",
        data=json.dumps(args.model_dump()).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=180) as response:
        result = json.load(response)

    answer = result.get("answer", "").strip()
    if not answer or answer.startswith(("Error:", "Service unavailable:")):
        raise RuntimeError(answer or "BrightPath API returned an empty answer")

    return {
        "answer": answer,
        "citations": result.get("citations", []),
        "kb_version": result.get("kb_version"),
    }