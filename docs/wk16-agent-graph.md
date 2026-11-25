# Week 16 — BrightPath Agent Graph

The graph scrubs the user's question before the first model call. It checks the remaining budget before each outer model or tool call. The budget uses simulated units; actual API cost is unmeasured.

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	think(think)
	tool(tool)
	iteration_limit(iteration_limit)
	pii_check(pii_check)
	cost_limit(cost_limit)
	__end__([<p>__end__</p>]):::last
	__start__ --> pii_check;
	cost_limit -. &nbsp;done&nbsp; .-> __end__;
	cost_limit -.-> think;
	cost_limit -.-> tool;
	pii_check --> cost_limit;
	think -. &nbsp;done&nbsp; .-> __end__;
	think -. &nbsp;check&nbsp; .-> cost_limit;
	tool -. &nbsp;check&nbsp; .-> cost_limit;
	tool -. &nbsp;limit&nbsp; .-> iteration_limit;
	iteration_limit --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```

Verification: `tests/test_wk16_graph.py` — 4 passed. See `eval/logs/wk16-graph-guardrails.txt`.
