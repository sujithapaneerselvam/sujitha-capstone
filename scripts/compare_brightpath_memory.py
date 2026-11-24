"""Live BrightPath memory ON/OFF comparison with resumable checkpoints."""
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agents.brightpath_agent import build_brightpath_agent
from src.agents.memory import MemoryStore
from src.agents.preference_memory import remember_format
from src.agents.mock_llm import OpenAILLM

GOLDEN = Path("data/brightpath_golden.jsonl")
OUTPUT = Path("eval/logs/wk15-brightpath-memory-full.json")

questions = [
    json.loads(line)
    for line in GOLDEN.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert len(questions) == 20, "Expected 20 BrightPath questions"
assert len({q["id"] for q in questions}) == 20, "Duplicate question IDs"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Resume completed runs instead of paying to repeat them.
rows = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else []
completed = {(r["id"], r["memory_on"]) for r in rows}

def save():
    OUTPUT.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

with TemporaryDirectory() as directory:
    db = Path(directory) / "memory.db"
    remember_format(MemoryStore(db), "eval-user", "bullets")

    for index, entry in enumerate(questions):
        # Alternate order to reduce a systematic OFF-first timing bias.
        modes = (False, True) if index % 2 == 0 else (True, False)

        for enabled in modes:
            if (entry["id"], enabled) in completed:
                continue

            print(
                f"\nRunning {entry['id']} | memory={enabled}",
                flush=True,
            )
            llm = OpenAILLM()
            agent = build_brightpath_agent(
                llm,
                memory_on=enabled,
                user_id="eval-user",
                db_path=db,
            )

            started = time.perf_counter()
            try:
                result = agent.run(entry["question"])
            except Exception as error:
                save()
                raise RuntimeError(
                    f"Stopped at {entry['id']}, memory={enabled}. "
                    "Earlier results are saved; fix the error and resume."
                ) from error

            elapsed = round((time.perf_counter() - started) * 1000)
            policy_steps = [
                step for step in result.steps
                if step.tool == "lookup_policy"
            ]

            row = {
                "id": entry["id"],
                "question": entry["question"],
                "ideal_answer": entry.get("ideal_answer"),
                "expected_source": entry.get("expected_source"),
                "memory_on": enabled,
                "router_model": getattr(llm, "model", "unknown"),
                "latency_ms": elapsed,
                "cost_usd": None,
                "policy_tool_called": bool(policy_steps),
                "policy_calls_ok": (
                    all(step.status == "ok" for step in policy_steps)
                    if policy_steps else None
                ),
                "review": {
                    "fact_correct": None,
                    "grounded": None,
                    "citation_valid": None,
                    "preference_met": None,
                    "notes": "",
                },
                "result": result.to_dict(),
            }
            rows.append(row)
            completed.add((entry["id"], enabled))
            save()

            print(result.answer, flush=True)
            print(
                "Statuses:",
                [(step.tool, step.status) for step in result.steps],
                flush=True,
            )
            print(f"Saved {len(rows)}/40 runs", flush=True)

            if any(step.status != "ok" for step in result.steps):
                for step in result.steps:
                    if step.status != "ok":
                        print(step.observation, flush=True)
                raise SystemExit(
                    "Stopped after a tool failure. The failed run is retained "
                    "as evidence. Fix the service before resuming."
                )

assert len(rows) == 40, f"Expected 40 runs, found {len(rows)}"
print("\nCOMPLETE:", OUTPUT.resolve())