# Phase 1 — Data Source Evaluation & Data Contracts

## Goal
Go beyond "find an API" — establish, in writing, exactly what can be relied on from each source before any ingestion code is written. This phase produces a **data contract** per source, not just a bookmark list.

## Generic activities
1. For each candidate source, identify: access method (REST API / bulk file download / database / scrape — prefer official APIs or bulk exports over scraping), auth requirement, cost (must be $0 or within budget), and license/usage terms.
2. Pull a real sample response/file and record the **actual** schema — not just what the docs say. Docs drift from reality more often than expected.
3. Document update frequency (real-time, daily, monthly, static) and compare it against the freshness requirement from Phase 0.
4. Document rate limits / quotas and estimate whether your expected call volume (given your scope — number of entities, time range) fits within them. Do this math explicitly; "should be fine" is not an estimate.
5. Assess breaking-change risk: is this a mature, versioned, well-documented API (low risk) or an informal/unofficial one (higher risk, plan for monitoring)?
6. If multiple sources need to be joined later, check they share (or can be mapped to) a common key (e.g. a shared entity ID, geography code, or timestamp granularity) — this is often discovered too late.

## Output
One data contract entry per source in `docs/data_contracts.md` (use `assets/data_contract_template.md`), each with: access method, auth, schema (with real sample), update frequency, rate limit + volume math, breaking-change risk, and shared-key compatibility notes.

## Tool-selection guidance
No single tool is "correct" here — the deliverable is a document, not code. A small verification script (any language) that calls each source once and prints the real response is worth writing before committing to the contract.

## AI usage tips
- This is one of the highest-leverage phases for AI: long, unevenly-organized API docs are exactly what a model is fast at summarizing.
- Ask AI to draft the rate-limit math and volume estimate, but verify the inputs (your actual scope numbers) yourself — a wrong assumption here compounds through later phases.
- Always run a live test call yourself rather than trusting a summarized schema outright; APIs change after any model's training cutoff.

## Feedback loop triggers
Revisit Phase 0 if a source can't deliver what a key analytical question needs (missing field, wrong granularity, insufficient history).
Revisit this file immediately if Phase 4 ingestion reveals the real response differs from what was documented here — don't let the contract go stale.

## Implementation patterns
- `assets/data_contract_template.md` — fill-in-the-blank template for each source
- `implementation/quality/data-quality-patterns.md` — data contract YAML specification (Pattern 5) for structured contract definitions
- `implementation/pipeline/pipeline-patterns.md` — ingestion patterns that depend on accurate source contracts
