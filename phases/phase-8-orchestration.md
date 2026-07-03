# Phase 8 — Orchestration

## Goal
Chain ingestion, transformation, and quality checks into a single automated, scheduled workflow with proper dependency handling and failure recovery.

## Generic activities
1. Assemble the individual tasks built in Phases 4-6 into a single DAG/workflow, with dependencies expressed explicitly (e.g. transformation tasks must wait for ingestion tasks to succeed, not just run in parallel and hope for the best).
2. Add retry policies and alerting on task failure — a pipeline that fails silently is worse than one that fails loudly.
3. Set the schedule based on the *real* update frequency of the slowest-updating source that matters (from the Phase 1 contract) — don't schedule hourly runs against a source that updates monthly.
4. Handle partial-availability cases explicitly if sources update on different cadences (e.g. skip-and-log logic when one source's new data isn't ready yet, rather than failing the whole run).

## Output
A single end-to-end workflow that runs successfully on trigger or schedule, covering ingestion through quality checks.

## AI usage tips
- AI is useful for DAG/workflow boilerplate and especially for branching/conditional logic (e.g. "skip this task if the upstream source hasn't updated") — this kind of conditional dependency logic is easy to get subtly wrong on a first attempt.

## Feedback loop triggers
If orchestrating the full pipeline surfaces timing conflicts between sources with different update cadences that weren't accounted for in Phase 1/2, update those documents rather than patching around it silently in the DAG.

## DESKILL Skills
This phase is implemented by:
- `/dag` → `skills/dag/SKILL.md` — builds orchestration DAG with dependencies, retry, scheduling, alerts

## Implementation patterns
- `implementation/orchestration/airflow-patterns.md` — complete Airflow patterns:
  - TaskFlow API for clean DAGs
  - Dynamic DAG generation from config
  - Branching and conditional logic
  - Sensors and external dependencies (S3, ExternalTask, custom API sensors)
  - Error handling and alerts (callbacks, Slack/PagerDuty)
  - DAG testing with pytest
- `implementation/pipeline/pipeline-patterns.md` — orchestration section for scheduling and workflow design
- `commands/data-pipeline.md` — orchestration section with Airflow and Prefect patterns
