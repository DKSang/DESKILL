# Data Engineering Anti-Patterns

Common mistakes that cause DE projects to fail silently. Each anti-pattern links to the DESKILL skill that prevents it.

---

## Discover Phase

### AP-1: Tool-first, problem-never
**Symptom:** "I want to learn Airflow/dbt/Spark, so I'll build a pipeline with them."
**Why it fails:** Pipeline runs but answers no real question. Portfolio reviewers see a tool demo, not engineering judgment.
**Fix:** `/problem` — define persona + analytical questions before touching tools.
**Red flag:** Business problem doc written after code exists.

### AP-2: Vague analytical questions
**Symptom:** "Understand trends in the data."
**Why it fails:** Cannot write SQL for "understand trends." No threshold, no entity, no timeframe.
**Fix:** `/problem` Step 3 — stress-test: "Can I write SQL for this today?"
**Red flag:** Question has no entity, metric, threshold, or timeframe.

### AP-3: Success metric = "pipeline runs"
**Symptom:** "Success is when the DAG completes without errors."
**Why it fails:** A pipeline that runs but produces wrong/stale data is worse than one that fails loudly.
**Fix:** `/problem` Step 4 — success metric must tie to answering questions within a freshness window.

---

## Data Contracts Phase

### AP-4: Trusting API docs for schema
**Symptom:** "The docs say the field is `price`, type string."
**Why it fails:** Docs are frequently out of date. Field may be renamed, removed, or typed differently.
**Fix:** `/sources` Step 2 — call the live API, paste actual response into contract.
**Red flag:** `lastVerified` date is missing or is the day you read the docs, not the day you called the API.

### AP-5: "Should be fine" rate limit math
**Symptom:** "500 calls/day should be enough."
**Why it fails:** No calculation. 10,000 stocks × 1 call = 10,000 calls. Free tier = 500.
**Fix:** `/sources` Step 3 — calculate volume per run, compare to limit, margin must be > 1.

### AP-6: No join key verification
**Symptom:** "Both sources have a ticker field, so they'll join."
**Why it fails:** Case sensitivity (`AAPL` vs `aapl`), format (`AAPL` vs `AAPL.US`), missing mapping table.
**Fix:** `/sources` Step 5 — verify join keys explicitly, document format differences.

---

## Architecture Phase

### AP-7: "Compare later" tool shopping
**Symptom:** "I'll list Airflow, Prefect, and Dagster and decide later."
**Why it fails:** Ambiguity blocks progress. Every downstream skill depends on this choice.
**Fix:** `/arch` Step 2 — pick exactly 1 tool per category with a reason. Revisit only if scale changes.

### AP-8: No scale assumption documented
**Symptom:** Architecture chosen without stating data volume.
**Why it fails:** DuckDB vs Spark, pandas vs distributed — the answer depends entirely on scale.
**Fix:** `/arch` Step 5 — document "pipeline processes ~X MB/day on a single machine."

### AP-9: Blank boxes in data flow diagram
**Symptom:** Diagram has "[Transform]" with no tool name.
**Why it fails:** Vague architecture leads to integration surprises.
**Fix:** `/arch` Step 3 — every box/arrow must have a specific tool name.

---

## Build Phase

### AP-10: One mega-script for all sources
**Symptom:** A single `ingest.py` handles all sources with if/else branches.
**Why it fails:** One source failing blocks all others. Hard to debug, impossible to scale independently.
**Fix:** `/ingest` — one script per source.

### AP-11: Business logic in Silver layer
**Symptom:** Silver model calculates `pct_change` or filters "active customers only."
**Why it fails:** Silver should be clean, not opinionated. Business rules change; Silver shouldn't.
**Fix:** `/transform` Step 1 — Silver does 4 things only: type cast, dedupe, handle nulls, join clean sources.

### AP-12: No DLQ for invalid records
**Symptom:** Invalid records crash the ingestion run.
**Why it fails:** One bad record kills the entire batch. No evidence of what went wrong.
**Fix:** `/ingest` Step 2 — route invalid records to DLQ, don't crash the run.

### AP-13: Testing logic vs. testing data confusion
**Symptom:** "I have dbt tests, so my data quality is covered."
**Why it fails:** dbt tests validate logic at code-change time. They don't catch runtime anomalies (source went stale, volume dropped).
**Fix:** `/test` (logic) + `/dq` (runtime) + `/contract-check` (contract compliance). Three distinct concerns.

---

## Quality Phase

### AP-14: AI-set DQ thresholds
**Symptom:** "AI suggested volume_min=5000."
**Why it fails:** AI doesn't know your domain. 5000 may be a crisis or normal.
**Fix:** `/dq` Step 2 — user must justify every threshold from domain knowledge or historical data.

### AP-15: Contract goes stale
**Symptom:** Source contract written once, never checked again.
**Why it fails:** Source changes schema silently. Code adapts quietly. Contract is now a lie.
**Fix:** `/contract-check` — auto-validate actual data vs contract after each ingestion run.

### AP-16: DQ checks that only log
**Symptom:** DQ check fails → `logger.warning("volume low")`.
**Why it fails:** No one reads logs proactively. Failures must alert.
**Fix:** `/dq` Step 3 — every failed check → log ERROR + trigger alert (Slack/email/PagerDuty).

---

## Ship Phase

### AP-17: DAG without retry policy
**Symptom:** Tasks have no `retries` configured.
**Why it fails:** Transient failures kill the entire pipeline run.
**Fix:** `/dag` Step 3 — retry policy on every task, not just ingestion.

### AP-18: Schedule faster than source updates
**Symptom:** Hourly DAG for a daily-updating source.
**Why it fails:** Wasted compute, redundant runs, no new data.
**Fix:** `/dag` Step 2 — schedule matches the slowest important source's update frequency.

### AP-19: Dashboard that answers nothing
**Symptom:** 10 pretty charts, none tied to an analytical question.
**Why it fails:** Polish without purpose. Portfolio reviewer sees noise.
**Fix:** `/serve` Step 1 — each chart answers exactly 1 question from `docs/business_problem.md`.

### AP-20: README without run commands
**Symptom:** README describes architecture but doesn't say how to run it.
**Why it fails:** Reviewer can't verify. Project looks incomplete.
**Fix:** `/docs` Step 1 — README must have exact `git clone → docker compose up → trigger DAG` commands.

### AP-21: Hardcoded secrets in CI
**Symptom:** `SOURCE_API_KEY=abc123` in `.github/workflows/ci.yml`.
**Why it fails:** Secret exposed in git history. Security incident.
**Fix:** `/ci` Step 3 — use GitHub Secrets, reference via `${{ secrets.SOURCE_API_KEY }}`.

---

## Cross-Cutting

### AP-22: Silent feedback loops
**Symptom:** `/ingest` reveals source can't provide a field. Developer patches code, doesn't update `/problem`.
**Why it fails:** Business problem doc now claims a question the pipeline can't answer.
**Fix:** Every skill's "Next Step" section includes feedback loop triggers. When a later phase invalidates an earlier decision, revise the earlier artifact — don't patch silently.

### AP-23: No metadata tags on Bronze
**Symptom:** Raw records lack `_loaded_at` and `_source`.
**Why it fails:** Silver can't do incremental loads. No lineage. Freshness checks impossible.
**Fix:** `/ingest` Step 2 — `_loaded_at` + `_source` on every record, must flow through to Gold.

### AP-24: Unpinned dependencies
**Symptom:** `requirements.txt` has `apache-airflow` (no version).
**Why it fails:** `pip install` today ≠ 3 months from now. Environment not reproducible.
**Fix:** `/env` Step 4 — pin every dependency to a specific version.

---

## How to Use This File

- **During `/problem`:** Check AP-1 through AP-3 before writing the problem doc.
- **During `/sources`:** Check AP-4 through AP-6 before finalizing contracts.
- **During `/arch`:** Check AP-7 through AP-9 before committing to a stack.
- **During build:** Check AP-10 through AP-13 at each skill.
- **During quality:** Check AP-14 through AP-16.
- **During ship:** Check AP-17 through AP-21.
- **Every skill:** Watch for AP-22 (silent feedback loops).

## References

- Root skill flow: `SKILL.md`
- Skill graph: `skills/skill-graph.json`
- Phase deep-dives: `phases/phase-*.md`
