# Incident: Old policy answer served after document update

**Summary:** A semantic-cache entry serves the previous parental-leave entitlement after the updated document was ingested.

## Symptoms

* Users receive “6 weeks paid + 6 weeks unpaid”; the current policy says “12 weeks paid + 4 weeks unpaid.”
* The affected response reports `cache_hit=True` and similarity at or above `0.95`.
* The document-update log reports successful tombstoning and ingestion.
* Six employees received the old answer this week.

## Likely root cause

The document update did not invalidate the semantic cache in `results.db`. A similar question matches an answer stored before Friday’s update, so `ask_rag()` returns it without retrieving the revised document. Confirm this by comparing cached and cache-bypassed calls. If both return the old entitlement, investigate the knowledge-base update instead.

## Diagnostic steps

Run from the repository root with the project environment loaded. Substitute the exact reported question if available.

```bash
python3 - <<'PY'
from src.rag.qdrant_rag import ask_rag

q = "What is the current parental leave entitlement?"
for label, use_cache in [("cached", True), ("live", False)]:
    r = ask_rag(q, use_cache=use_cache)
    print(label, "cache_hit=", r["cache_hit"], "answer=", r["answer"])
PY
```

Expected for this incident: the cached call returns the old entitlement; the live call returns 12 paid and 4 unpaid weeks. The live call bypasses the semantic cache.

```bash
python3 - <<'PY'
from src.rag import cache
print(cache.stats("./results.db"))
PY
```

Expected: at least one cache entry. Check the same database path used by `ask_rag()`.

```bash
python3 - <<'PY'
import sqlite3
from datetime import datetime, timezone

with sqlite3.connect("./results.db") as con:
    rows = con.execute(
        "SELECT question, answer, created_ts FROM query_cache "
        "WHERE lower(question) LIKE '%parental%' "
        "ORDER BY created_ts DESC"
    ).fetchall()
for question, answer, created in rows:
    print(datetime.fromtimestamp(created, timezone.utc), question, answer)
PY
```

Expected: an old entitlement in a row created before Friday’s document update. A paraphrased user question may match a differently worded cached question.

## Fix

After confirming the live answer is correct, clear only the semantic cache:

```bash
python3 - <<'PY'
from src.rag import cache
print("Entries removed:", cache.clear("./results.db"))
print("Cache after:", cache.stats("./results.db"))
PY
```

Expected: `n_entries` is `0`. Do not reset Qdrant or re-ingest the corpus.

## Verification

Ask the reported question twice:

```bash
python3 - <<'PY'
from src.rag.qdrant_rag import ask_rag

q = "What is the current parental leave entitlement?"
for label in ("first", "second"):
    r = ask_rag(q, use_cache=True)
    print(label, "cache_hit=", r["cache_hit"], "answer=", r["answer"])
PY
```

Confirm the first call is a miss, both answers state 12 paid and 4 unpaid weeks, and the second call is a hit. Repeat with the exact wording reported by the HR partner before closing.

## Post-incident actions

1. Make cache clearing the default on every successful document update; add a CI check for update paths that bypass it.
2. Notify the HR partner and six affected employees of the corrected entitlement and ask them to disregard the earlier answer.
3. Monitor sampled cache hits against cache-bypassed answers after policy updates; investigate sustained unusually high hit rates.

**Time budget:** Approximately 8 minutes to diagnose, 3 minutes to clear and verify, and 15 minutes for communication and follow-up.
