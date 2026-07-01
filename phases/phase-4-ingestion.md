# Phase 4 — Ingestion (Bronze / Raw Layer)

## Goal
Move data from each source into raw storage reliably, preserving original structure — without doing any cleaning or business logic yet.

## Generic activities
1. Build one ingestion script/task per source (not one script trying to handle all sources generically too early — separate concerns first, unify later only if there's real duplication).
2. Start with a small subset of the full scope (a few entities, a short date range) to validate the ingestion logic before scaling to the full scope defined in Phase 0. This catches bugs cheaply.
3. Each ingestion run should: call/read the source → do a light validation (status code, non-empty response, basic schema check against the Phase 1 contract) → write raw output to storage, partitioned in a way that supports incremental loads (e.g. by date).
4. Add basic resilience: retries with backoff for transient failures, and logging that makes failures diagnosable without re-running blind.
5. Tag raw records with metadata useful downstream: ingestion timestamp, source identifier, and (if relevant) the specific request parameters used.
6. Once the small-scope version is verified end-to-end, scale up to the full scope from Phase 0.

## Output
Raw/Bronze storage populated with real data from every source, covering enough history/breadth to meaningfully test transformations in Phase 5.

## AI usage tips
- AI is efficient at generating the repetitive parts: retry/backoff logic, logging boilerplate, and basic response validation.
- When a source's real response doesn't match what Phase 1 documented, paste the actual error/response to AI for fast diagnosis — but update `data_contracts.md` yourself once resolved.

## Feedback loop triggers
This is the phase most likely to reveal that Phase 1's contract was incomplete or wrong (field names differ, pagination undocumented, rate limits stricter in practice). Update Phase 1's document immediately, don't let the discrepancy live only in your memory or in scattered code comments.
If the full-scope ingestion is infeasible (rate limits, volume, cost), revisit Phase 0's scope before forcing a workaround.

## Implementation patterns
- `implementation/pipeline/pipeline-patterns.md` — batch and streaming ingestion patterns with retry logic, dead letter queues, metadata tracking
- `implementation/transformation/dbt-patterns.md` — source definitions and staging models that consume raw data
- `commands/data-pipeline.md` — ingestion implementation section (batch incremental loading, streaming with exactly-once semantics)
