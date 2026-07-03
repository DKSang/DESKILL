# Phase 2 — Architecture Design

## Goal
Decide how raw data becomes a queryable analytics layer, and commit to ONE stack rather than listing every tool in a category "just in case." Ambiguity here is the single biggest cause of stalled portfolio projects.

## Generic activities
1. Choose a layering strategy. Medallion (Bronze/Silver/Gold) is a common default, but the point is having *any* clear separation between raw, cleaned, and business-ready data — not the specific names.
2. For each layer, write down its contract: what goes in, what transformation is (and isn't) allowed, what the output guarantees.
3. Pick exactly one tool per category — do not list 4 orchestrators "to compare later." Categories to decide:
   - Orchestration (e.g. Airflow, Dagster, Prefect — pick one)
   - Object/file storage (e.g. MinIO for local S3-compatible storage, or a cloud bucket)
   - Transformation (e.g. dbt, Spark, plain Python/pandas — driven by data volume and job-market relevance)
   - Query engine / warehouse (e.g. DuckDB for local/small-scale, or a cloud warehouse for larger scale)
   - Containerization (e.g. Docker Compose for local reproducibility)
4. Draw the architecture: sources → ingestion → Bronze → Silver → Gold → serving, with the chosen tool named at each arrow.
5. Define naming conventions for schemas/tables now (e.g. `bronze.<entity>_raw`, `silver.<entity>_clean`, `gold.<entity>_<grain>`) — retrofitting naming later is painful.
6. Note the scale assumption explicitly (e.g. "hundreds of MB, single machine" vs "needs distributed compute") — this justifies every tool choice above and should be revisited if scope changes.

## Output
`docs/architecture.md` + one diagram (any tool: Excalidraw, draw.io, or a Claude-generated diagram) showing the layered flow with named tools.

## Tool-selection guidance
Prefer boring, well-documented tools for a portfolio project over exotic ones — the goal is to demonstrate sound engineering judgment, and "I chose X because it fit the scale and is what employers in this space commonly use" is a stronger interview answer than "I used every tool I could fit in."

## AI usage tips
- Use AI as a rubber duck for architecture review: "what would break if I scaled this 10x / added a second data domain?"
- Ask AI to list the failure modes of your chosen stack (not to talk you out of it, but so you know them going in).

## Feedback loop triggers
Revisit if Phase 4/5 reveal the chosen transformation tool can't handle the actual data volume or shape, or if a source's format (Phase 1) doesn't fit cleanly into the planned Bronze layer contract.

## DESKILL Skills
This phase is implemented by:
- `/arch` → `skills/arch/SKILL.md` — designs pipeline architecture, picks 1 tool per category
- `/schema` → `skills/schema/SKILL.md` — designs DW schema (Fact/Dim tables, grain)

## Implementation patterns
- `implementation/pipeline/pipeline-patterns.md` — architecture patterns (ETL/ELT/Lambda/Kappa/Lakehouse)
- `implementation/orchestration/airflow-patterns.md` — if Airflow is the chosen orchestrator
- `implementation/transformation/dbt-patterns.md` — if dbt is the chosen transformation tool
- `implementation/optimization/spark-patterns.md` — if Spark is needed for scale
- `agents/data-engineer.md` — AI agent persona for architecture design discussions
- `agents/backend-architect.md` — AI agent persona for backend/serving layer design
