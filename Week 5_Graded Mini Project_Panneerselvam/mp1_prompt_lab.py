"""Week 5 MP1: compare four prompting strategies on job extraction.

Put OPENAI_API_KEY in .env, then run: python mp1_prompt_lab.py
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from openai import AsyncOpenAI

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL = "gpt-4o-mini"
JUDGE_MODEL = "gpt-4o"
TEMPERATURE = 0.0
RATES = {
    "gpt-4o-mini": {"in": 0.15 / 1_000_000, "out": 0.60 / 1_000_000},
    "gpt-4o": {"in": 2.50 / 1_000_000, "out": 10.00 / 1_000_000},
}

# These are set in main() before any API calls are made.
client: AsyncOpenAI
call_gate: asyncio.Semaphore
judge_gate: asyncio.Semaphore
snippets: list[dict]


def task_text(snippet_text: str) -> str:
    return (
        "Extract company, role, and minimum years of experience from this job posting. "
        "Return only JSON with exactly these fields: "
        '{"company": string, "role": string, "years_experience_required": integer or null}. '
        "Use the lower value of a range. If years are not stated, return null; do not guess.\n\n"
        "Job posting:\n" + snippet_text
    )


def prompt_zero_shot(snippet_text: str) -> list[dict]:
    """Strategy 1 — zero-shot. Just ask, no examples, no persona."""
    # Return one direct instruction with no examples or role description.
    return [{"role": "user", "content": task_text(snippet_text)}]


def prompt_few_shot(snippet_text: str) -> list[dict]:
    """Strategy 2 — few-shot. Include 2-3 worked examples in the prompt."""
    # Include examples so the model can see the expected extraction format.
    examples = (
        "Examples:\n"
        'Posting: Bright Labs is hiring a Backend Engineer. Candidates need 4+ years of Python experience.\n'
        'JSON: {"company":"Bright Labs","role":"Backend Engineer","years_experience_required":4}\n\n'
        "Posting: Green Leaf needs a Junior Designer. Fresh graduates are welcome; no previous experience is required.\n"
        'JSON: {"company":"Green Leaf","role":"Junior Designer","years_experience_required":0}\n\n'
        "Posting: Atlas Health seeks a Data Scientist. A PhD is preferred, but no years are stated.\n"
        'JSON: {"company":"Atlas Health","role":"Data Scientist","years_experience_required":null}\n\n'
    )
    return [{"role": "user", "content": examples + task_text(snippet_text)}]


def prompt_structured(snippet_text: str) -> list[dict]:
    """Strategy 3 — structured / role-based. Use a system prompt with a persona and explicit JSON schema."""
    # Give the model a recruiter role and a clear JSON-only response contract.
    system = (
        "You are an expert recruitment operations analyst. Extract only facts explicitly stated. "
        "Return valid JSON only with exactly company, role, and years_experience_required. "
        "years_experience_required must be an integer or null. Never infer years from seniority, "
        "education, skills, or usual industry expectations."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": task_text(snippet_text)}]


def prompt_cot(snippet_text: str) -> list[dict]:
    """Strategy 4 — chain-of-thought. Ask the model to reason before answering."""
    # Ask it to check the details silently, but return only the final JSON.
    content = (
        "Reason silently: identify the hiring organisation, exact job title, and minimum explicit years. "
        "Do not reveal reasoning. Return only JSON with company, role, and years_experience_required; "
        "use null when years are not stated.\n\nJob posting:\n" + snippet_text
    )
    return [{"role": "user", "content": content}]


STRATEGIES = {
    "zero_shot": prompt_zero_shot,
    "few_shot": prompt_few_shot,
    "structured": prompt_structured,
    "cot": prompt_cot,
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_response(text: str) -> dict | None:
    """Try to parse a JSON object out of the model's response. Return None if it doesn't parse.

    Hint: models sometimes wrap JSON in ```json ... ``` fences. Strip them first.
    """
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    if text.endswith(fence):
        text = text[:-3].strip()
    try:
        item = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            return None
        try:
            item = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return item if isinstance(item, dict) else None


def norm_text(value: Any) -> str | None:
    return None if value is None else " ".join(str(value).strip().casefold().split())


def norm_years(value: Any) -> int | None | str:
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    match = re.fullmatch(r"\s*(\d+)\s*\+?\s*", str(value))
    return int(match.group(1)) if match else "invalid"


def normalise(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if not value:
        return None
    aliases = {
        "company": ("company", "company_name"),
        "role": ("role", "job_role", "job_title", "title"),
        "years_experience_required": ("years_experience_required", "years_required", "experience_years"),
    }
    output = {key: next((value[name] for name in names if name in value), None) for key, names in aliases.items()}
    output["company"] = norm_text(output["company"])
    output["role"] = norm_text(output["role"])
    output["years_experience_required"] = norm_years(output["years_experience_required"])
    return output


def cost(model: str, usage: Any) -> float:
    if not usage:
        return 0.0
    return usage.prompt_tokens * RATES[model]["in"] + usage.completion_tokens * RATES[model]["out"]


async def run_one(strategy_name: str, snippet: dict) -> dict:
    """Run one strategy on one snippet. Return a dict with all the captured fields."""
    started = time.perf_counter()
    try:
        async with call_gate:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=STRATEGIES[strategy_name](snippet["snippet"]),
                temperature=TEMPERATURE,
            )
        raw = response.choices[0].message.content or ""
        parsed = parse_response(raw)
        return {
            "strategy": strategy_name, "snippet_id": snippet["id"], "snippet": snippet["snippet"],
            "raw_response": raw, "extracted": normalise(parsed), "parse_success": parsed is not None,
            "cost_usd": cost(MODEL, response.usage), "latency_s": time.perf_counter() - started, "error": None,
        }
    except Exception as exc:
        return {
            "strategy": strategy_name, "snippet_id": snippet["id"], "snippet": snippet["snippet"],
            "raw_response": "", "extracted": None, "parse_success": False, "cost_usd": 0.0,
            "latency_s": time.perf_counter() - started, "error": type(exc).__name__ + ": " + str(exc),
        }


async def run_all() -> list[dict]:
    """Run all 10 × 4 = 40 calls in parallel. Use asyncio.gather."""
    # Build one task for each strategy and each job posting.
    tasks = [run_one(strategy_name, snippet) for strategy_name in STRATEGIES for snippet in snippets]
    return await asyncio.gather(*tasks)


def score_accuracy(extracted: dict | None, gold: dict) -> int:
    """Compare 3 fields. Case-insensitive, whitespace-trimmed for strings. Return 0, 1, 2, or 3."""
    if extracted is None:
        return 0
    extracted = normalise(extracted)
    expected = normalise(gold)
    if extracted is None or expected is None:
        return 0
    return sum(extracted[field] == expected[field] for field in ("company", "role", "years_experience_required"))


async def score_llm_judge(snippet_text: str, extracted: dict | None, gold: dict) -> dict:
    """Use gpt-4o as a judge. Return the judge score, reason, and cost."""
    prompt = (
        "You are a strict evaluator of job-posting extraction.\n\nPosting:\n" + snippet_text +
        "\n\nReference: " + json.dumps(normalise(gold)) +
        "\nCandidate: " + json.dumps(extracted) +
        "\n\nScore 1-4: 4=all fields correct; 3=two fields correct and no fabricated experience; "
        "2=one field correct or fabricated years when reference is null; 1=none correct or unparsable. "
        'Return only JSON with fields score and reason.'
    )
    try:
        async with judge_gate:
            response = await client.chat.completions.create(
                model=JUDGE_MODEL, messages=[{"role": "user", "content": prompt}], temperature=TEMPERATURE
            )
        parsed = parse_response(response.choices[0].message.content or "") or {}
        score = max(1, min(4, int(parsed.get("score", 1))))
        return {"llm_judge_score": score, "judge_reason": parsed.get("reason", ""), "judge_cost_usd": cost(JUDGE_MODEL, response.usage)}
    except Exception as exc:
        return {"llm_judge_score": 1, "judge_reason": "Judge error: " + type(exc).__name__, "judge_cost_usd": 0.0}


async def judge_all(results: list[dict[str, Any]], golden: dict[str, dict[str, Any]]) -> None:
    tasks = [score_llm_judge(item["snippet"], item["extracted"], golden[item["snippet_id"]]) for item in results]
    for item, judgement in zip(results, await asyncio.gather(*tasks)):
        item.update(judgement)


def build_summary(scored: list[dict]) -> pd.DataFrame:
    """Build the comparison table from the scored results."""
    df = pd.DataFrame(scored)

    # Include both the extraction call and the LLM-as-a-judge call in the cost.
    df["total_cost_usd"] = df["cost_usd"] + df["judge_cost_usd"]

    summary = df.groupby("strategy", sort=False).agg({
        "accuracy": "mean",
        "parse_success": "mean",
        "llm_judge_score": "mean",
        "total_cost_usd": "sum",
        "latency_s": "median",
        "error": lambda values: sum(value is None for value in values),
    }).round(6)

    summary.columns = [
        "accuracy_mean",
        "parse_rate",
        "judge_score_mean",
        "total_cost_usd",
        "latency_p50_s",
        "successful_calls",
    ]
    return summary.reset_index()


def write_reports(table: pd.DataFrame, results: list[dict[str, Any]]) -> None:
    display = table[["strategy", "accuracy_mean", "parse_rate", "judge_score_mean", "total_cost_usd", "latency_p50_s", "successful_calls"]].copy()
    display.columns = ["Strategy", "Accuracy", "Parse rate", "LLM judge", "Total cost", "Latency p50", "Successful calls"]
    display["Accuracy"] = display["Accuracy"].map(lambda item: "{:.2f} / 3".format(item))
    display["Parse rate"] = display["Parse rate"].map(lambda item: "{:.0%}".format(item))
    display["LLM judge"] = display["LLM judge"].map(lambda item: "{:.2f} / 4".format(item))
    display["Total cost"] = display["Total cost"].map(lambda item: "USD {:.6f}".format(item))
    display["Latency p50"] = display["Latency p50"].map(lambda item: "{:.3f}s".format(item))
    j10 = [item for item in results if item["snippet_id"] == "j10"]
    j10_notes = "\n".join(
        "- {}: years = {}, accuracy = {}/3, judge = {}/4.".format(
            item["strategy"],
            item["extracted"]["years_experience_required"] if item["extracted"] else None,
            item["accuracy"], item["llm_judge_score"]
        )
        for item in j10
    )
    (BASE_DIR / "mp1_comparison.md").write_text(
        "# MP1 Prompt Strategy Comparison\n\n"
        "All four strategies used gpt-4o-mini at temperature 0.0. Each was scored on the same 10 job postings.\n\n"
        + display.to_markdown(index=False) + "\n\n"
        "## J10 null-value check\n\n"
        "J10 does not state years of experience. The correct value is null; any number is a hallucination.\n\n"
        + j10_notes + "\n",
        encoding="utf-8",
    )
    winner = table.sort_values(["accuracy_mean", "parse_rate", "judge_score_mean"], ascending=False).iloc[0]
    wrong = [item["strategy"] for item in j10 if not item["extracted"] or item["extracted"]["years_experience_required"] is not None]
    observation = (
        "The J10 null-value edge case was handled incorrectly by {}. This shows where the prompt encouraged the model to invent information not present.".format(", ".join(wrong))
        if wrong else
        "All four strategies preserved the null value in J10, showing that the explicit null instruction was effective."
    )
    writeup = (
        "# MP1 Reflection — Prompt Strategy Comparison\n\n"
        "## Which strategy performed best?\n\n"
        "The **{}** strategy performed best in this run, with an accuracy of {:.2f}/3, a parse rate of {:.0%}, and an LLM-as-a-judge score of {:.2f}/4. "
        "I selected the winner by considering field-level accuracy first, then parse reliability and judge quality. This ordering matters because an extraction system is useful only when it returns the correct values in a form that a downstream program can consume reliably. "
        "Cost and latency were also recorded so that the recommendation is not based on output quality alone.\n\n"
        "## What surprised me?\n\n"
        "{} This reinforced that a response can sound helpful to a person but still be unsuitable for an application when it is not valid JSON or when a required field has the wrong type. "
        "The J10 case is particularly important: the job posting does not state a minimum experience requirement, so null is the correct answer. Returning a plausible number would look complete, but it would be a hallucination and would reduce trust in the system.\n\n"
        "## Which strategy would I use for my capstone?\n\n"
        "For my Enterprise Knowledge Assistant capstone, I would start with the structured / role-based strategy. "
        "The capstone needs consistent fields, citations, confidence, and clear escalation behaviour, so an explicit output contract is safer than a loose conversational prompt. "
        "I would retain a small number of relevant few-shot examples if they improve difficult cases, but I would keep the output instructions simple and validate every response before displaying it to a user.\n\n"
        "## What would I try next?\n\n"
        "With another day, I would add more ambiguous examples, analyse accuracy separately for each field, and run the judge multiple times to measure judge variance. "
        "I would also compare a schema-only prompt with the winning strategy before adopting it for the capstone. Finally, I would create targeted tests for missing experience values, ranges such as 3–5 years, and expressions such as 5+ years. "
        "Those tests would make the evaluation more representative of the imperfect language that a real knowledge assistant must handle.\n"
    ).format(winner["strategy"], winner["accuracy_mean"], winner["parse_rate"], winner["judge_score_mean"], observation)
    (BASE_DIR / "mp1_writeup.md").write_text(writeup, encoding="utf-8")


async def main() -> None:
    global client, call_gate, judge_gate, snippets
    load_dotenv(BASE_DIR / ".env")
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env and run again.")
    snippets = load_jsonl(DATA_DIR / "job_snippets.jsonl")
    golden = {item["id"]: item for item in load_jsonl(DATA_DIR / "golden_set.jsonl")}
    client = AsyncOpenAI()
    call_gate = asyncio.Semaphore(10)
    judge_gate = asyncio.Semaphore(10)
    print("Running {} x {} = 40 gpt-4o-mini extraction calls...".format(len(snippets), len(STRATEGIES)))
    results = await run_all()
    print(f"Got {len(results)} results.")
    print(results[0])

    # Apply scoring to all 40 results.
    scored = []
    for item in results:
        item["accuracy"] = score_accuracy(item["extracted"], golden[item["snippet_id"]])
        scored.append(item)
    print(f"Scored {len(scored)} results.")
    print("Running 40 gpt-4o LLM-as-a-judge calls...")
    await judge_all(scored, golden)
    table = build_summary(scored)
    (BASE_DIR / "results.json").write_text(json.dumps(scored, indent=2), encoding="utf-8")
    pd.DataFrame(scored).drop(columns=["snippet"], errors="ignore").to_csv(BASE_DIR / "results.csv", index=False)
    write_reports(table, scored)
    print(table[["strategy", "accuracy_mean", "parse_rate", "judge_score_mean", "total_cost_usd", "latency_p50_s"]].to_string(index=False))
    print("\nCreated results.json, results.csv, mp1_comparison.md and mp1_writeup.md.")


if __name__ == "__main__":
    asyncio.run(main())