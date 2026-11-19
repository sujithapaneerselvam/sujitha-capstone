"""Week 13 tool-design clinic.

Examples:
    python3 scripts/tool_clinic.py list
    python3 scripts/tool_clinic.py run C1
    python3 scripts/tool_clinic.py grade C1 naming
    python3 scripts/tool_clinic.py lint C1
    python3 scripts/tool_clinic.py lint good
"""
import argparse
import re

PRINCIPLES = ("naming", "schema", "description", "idempotency")

WEATHER_DESCRIPTION = (
    "Use this to get current weather for a city. Returns temperature "
    "and conditions. Do not use for forecasts."
)

CASES = {
    "C1": {
        "name": "data",
        "description": WEATHER_DESCRIPTION,
        "parameters": {"city": {"type": "string"}},
        "required": ["city"],
        "idempotent": True,
        "has_side_effects": False,
        "symptom": "Rarely selected, or selected for the wrong requests.",
        "principle": "naming",
        "why": "The name is a vague noun rather than a specific action.",
        "fix": "Rename it get_weather.",
    },
    "C2": {
        "name": "get_weather",
        "description": WEATHER_DESCRIPTION,
        "parameters": {"city": {}},
        "required": ["city"],
        "idempotent": True,
        "has_side_effects": False,
        "symptom": "Wrong or missing arguments cause runtime failures.",
        "principle": "schema",
        "why": "The city parameter has no declared type.",
        "fix": "Use typed Pydantic fields and declare required inputs.",
    },
    "C3": {
        "name": "get_order_status",
        "description": "Gets the status.",
        "parameters": {"order_id": {"type": "string"}},
        "required": ["order_id"],
        "idempotent": True,
        "has_side_effects": False,
        "symptom": "The model cannot tell when to choose this tool.",
        "principle": "description",
        "why": "The description does not explain when to use the tool.",
        "fix": "Explain when to use it, its output, and its limits.",
    },
    "C4": {
        "name": "send_notification",
        "description": (
            "Use this to send a notification to one recipient. Returns "
            "delivery status. Do not use for reading notifications."
        ),
        "parameters": {
            "recipient": {"type": "string"},
            "message": {"type": "string"},
        },
        "required": ["recipient", "message"],
        "idempotent": True,
        "has_side_effects": True,
        "deduplicated": False,
        "symptom": "Retries after a timeout send duplicate notifications.",
        "principle": "idempotency",
        "why": "Sending without deduplication is incorrectly marked idempotent.",
        "fix": "Mark non-idempotent; add deduplication before automatic retries.",
    },
    "C5": {
        "name": "handle",
        "description": (
            "Use this for weather lookup, currency conversion, or notifications. "
            "Returns the selected operation's result. Do not use for other tasks."
        ),
        "parameters": {
            "operation": {"type": "string"},
            "value": {"type": "string"},
        },
        "required": ["operation", "value"],
        "idempotent": False,
        "has_side_effects": True,
        "symptom": "One tool does three jobs and is selected unpredictably.",
        "principle": "naming",
        "why": "A generic name hides several unrelated responsibilities.",
        "fix": "Split into single-purpose tools with specific action names.",
    },
    "C6": {
        "name": "search_documents",
        "description": "Use this to answer ANY question about anything.",
        "parameters": {"query": {"type": "string"}},
        "required": ["query"],
        "idempotent": True,
        "has_side_effects": False,
        "symptom": "Selected for almost everything, crowding out other tools.",
        "principle": "description",
        "why": "The description claims an unlimited scope.",
        "fix": "State its actual scope and when not to use it.",
    },
}

GOOD = [
    {
        "name": "search_web",
        "description": (
            "Use this for current public information. Returns web snippets. "
            "Do not use for internal company documents or arithmetic."
        ),
        "parameters": {
            "query": {"type": "string"},
            "max_results": {"type": "integer", "default": 3},
        },
        "required": ["query"],
        "idempotent": True,
        "has_side_effects": False,
    },
    {
        "name": "query_sql",
        "description": (
            "Use this for read-only queries over document metadata. Returns "
            "matching rows. Do not use for writes or interpreting policy text."
        ),
        "parameters": {"sql": {"type": "string"}},
        "required": ["sql"],
        "idempotent": True,
        "has_side_effects": False,
    },
    {
        "name": "calculate",
        "description": (
            "Use this for exact arithmetic. Returns the numeric result. "
            "Do not use to retrieve facts or company policies."
        ),
        "parameters": {"expression": {"type": "string"}},
        "required": ["expression"],
        "idempotent": True,
        "has_side_effects": False,
    },
]


def lint(tool):
    """Teaching heuristics, not a production safety validator."""
    name = tool.get("name", "")
    description = tool.get("description", "").lower()
    parameters = tool.get("parameters", {})
    required = tool.get("required", [])

    return {
        "naming": (
            bool(re.fullmatch(r"[a-z][a-z0-9_]*", name))
            and name not in {"data", "handle", "process"}
        ),
        "schema": (
            bool(parameters)
            and all(
                spec.get("type") in {
                    "string", "integer", "number", "boolean", "array", "object"
                }
                and (key in required or "default" in spec)
                for key, spec in parameters.items()
            )
            and all(key in parameters for key in required)
        ),
        "description": (
            "use this" in description
            and "returns" in description
            and "do not" in description
            and "any question" not in description
        ),
        "idempotency": (
            isinstance(tool.get("idempotent"), bool)
            and isinstance(tool.get("has_side_effects"), bool)
            and not (
                tool["idempotent"]
                and tool["has_side_effects"]
                and not tool.get("deduplicated", False)
            )
        ),
    }


def show_lint(tool):
    print(f"\nLint: {tool['name']}")
    checks = lint(tool)
    for principle, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {principle}")
    return all(checks.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list")
    run = commands.add_parser("run")
    run.add_argument("case", choices=CASES)

    grade = commands.add_parser("grade")
    grade.add_argument("case", choices=CASES)
    grade.add_argument("principle", choices=PRINCIPLES)

    lint_command = commands.add_parser("lint")
    lint_command.add_argument("case", choices=[*CASES, "good"])

    args = parser.parse_args()

    if args.command == "list":
        for case_id, case in CASES.items():
            print(f"{case_id}: {case['name']} — {case['symptom']}")
        return 0

    if args.command == "lint":
        tools = GOOD if args.case == "good" else [CASES[args.case]]
        passed = [show_lint(tool) for tool in tools]
        return 0 if all(passed) else 1

    case = CASES[args.case]

    if args.command == "run":
        print(f"{args.case}: {case['name']}")
        print("Symptom:", case["symptom"])
        for field in (
            "description", "parameters", "required",
            "idempotent", "has_side_effects",
        ):
            print(f"{field}: {case[field]}")
        return 0

    if args.principle != case["principle"]:
        print("Incorrect. Inspect the definition again.")
        return 1

    print(f"Correct — {case['principle']}")
    print("Why:", case["why"])
    print("Fix:", case["fix"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())