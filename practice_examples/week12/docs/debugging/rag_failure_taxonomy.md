# RAG Failure Taxonomy — four primary runtime buckets

retrieval · generation · prompt · infra — these localise a *runtime* failure from a
trace. Beyond the runtime pipeline, cross-cutting failures — ingestion/data-quality,
access & security, evaluation/reference defects, and user-input/policy — live upstream
or across stages and are diagnosed elsewhere (W8, W11).
