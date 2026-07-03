# Phase 5 — Transformation (Silver/Gold) + Pipeline Testing

## Goal
Turn raw data into trustworthy, analysis-ready tables — and prove the transformation *logic* is correct through tests, as a distinct concern from validating the data itself (that's Phase 6).

## Generic activities — Transformation
1. Raw → cleaned layer: standardize types, deduplicate, handle nulls explicitly (don't let a default "drop nulls" decision hide a real data problem), and join sources on the shared key identified in Phase 1.
2. Cleaned → business/analytics layer: aggregate to the grain the analytical questions from Phase 0 actually need (not finer or coarser than necessary), and compute any derived metrics those questions require.
3. Keep each transformation step small and named clearly enough that someone could trace a wrong number in the final table back to the specific step that produced it.

## Generic activities — Testing (logic correctness, checked at code-change time)
1. Schema-level tests: not-null / uniqueness / accepted-value checks on key columns of every model.
2. Logic-level tests: for any non-trivial calculation (rolling windows, custom aggregations, business rules), write a small test with known input → known expected output.
3. Run this test suite every time transformation code changes, ideally automatically (see Phase 9 for CI).

## Output
Final analytics-ready table(s) matching the grain and columns the Phase 0 questions need, with a passing test suite covering schema and logic correctness.

## AI usage tips
- AI is strong at translating a described business rule into working SQL/Python — but window functions, rolling calculations, and edge-case handling (first/last record in a window, ties, missing periods) are exactly where AI-generated logic most often has subtle off-by-one or boundary errors. Review these by hand with a concrete example, don't just trust that tests passing means correct — write the test cases yourself or verify AI-generated ones against manually worked examples.
- Use AI to brainstorm edge cases you might not think of (empty groups, duplicate timestamps, out-of-order records).

## Feedback loop triggers
If a transformation can't produce what an analytical question (Phase 0) needs even with correct logic — because the necessary granularity or field simply isn't in the source — that's a Phase 0/1 problem, not something to force-fix here.

## DESKILL Skills
This phase is implemented by:
- `/transform` → `skills/transform/SKILL.md` — builds Silver (cleaned) and Gold (analytics-ready) models
- `/test` → `skills/test/SKILL.md` — writes schema + logic test suite (validates logic at code-change time)

## Implementation patterns
- `implementation/transformation/dbt-patterns.md` — complete dbt patterns: staging models, intermediate models, mart models (dimensions + facts), incremental strategies, macros
- `implementation/optimization/spark-patterns.md` — Spark transformation patterns if using distributed compute
- `implementation/quality/data-quality-patterns.md` — dbt test patterns (generic + singular tests) that validate transformation logic
