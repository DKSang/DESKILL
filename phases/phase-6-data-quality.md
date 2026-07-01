# Phase 6 — Data Quality & Observability

## Goal
Validate the actual data produced at runtime — distinct from Phase 5's validation of transformation logic. Even perfectly correct logic can produce bad output if the input data itself is anomalous.

## Generic activities
1. Freshness checks: is new data arriving on the expected cadence (from the Phase 1 contract)? Alert if a source goes stale beyond a reasonable threshold.
2. Volume checks: does the row count per run fall within an expected range? A sudden drop or spike is often the first sign of an upstream problem.
3. Schema-drift checks: has a source silently added/removed/renamed a field? (This is where Phase 1's documented contract earns its value — you have something concrete to check against.)
4. Distribution/anomaly checks calibrated with actual domain knowledge — e.g. what counts as an unusual value depends entirely on the domain, and this threshold should come from the user's understanding, not a generic AI guess.
5. Set up lightweight alerting (a log, a file, a webhook — doesn't need to be sophisticated for a portfolio project) so failures are visible without manually checking.

## Output
A small report or dashboard showing data quality status over time, plus a documented set of checks with their thresholds and rationale.

## AI usage tips
- Ask AI to propose a starting set of checks based on the table schema, then adjust every threshold based on real domain knowledge — AI doesn't know what's a normal vs. anomalous value in your specific domain.

## Feedback loop triggers
If quality checks keep failing on legitimate data (false positives), the thresholds — not the data — are usually wrong; revisit them with real historical data rather than loosening them arbitrarily.

## Implementation patterns
- `implementation/quality/data-quality-patterns.md` — complete quality framework with:
  - Great Expectations suites (schema, PK, FK, categorical, numeric, date, freshness, row count, statistical)
  - Great Expectations checkpoints with Slack notifications
  - dbt data tests (schema tests, recency, relationships, accepted values)
  - Custom dbt tests (row_count_in_range, sequential_values)
  - Data contracts YAML specification
  - Automated quality pipeline orchestrator in Python
