# RAG Debugging Runbook

Reproduce -> Narrow (get the trace) -> Isolate (first stage whose output is wrong)
-> Fix (smallest change for that bucket; treat retrieval changes as candidates you
test against the golden set) -> Verify (re-run the whole eval suite).
