---
description: "Deploy pipeline, orchestrate, document, and hand off"
---

# Data Engineering — Ship Command

Package, deploy, and document the pipeline. Run AFTER `/review`.

## Instructions

### 1. Orchestration

- [ ] Assemble ingestion + transformation + quality into one DAG/workflow
- [ ] Dependencies are explicit (transform waits for ingest)
- [ ] Retry policies and alerting configured
- [ ] Schedule matches the slowest source update frequency
- [ ] Partial-availability handled (skip-and-log, not full failure)

### 2. Serving Layer

- [ ] One view/dashboard per analytical question from `/spec`
- [ ] Correctness over polish
- [ ] Demo captured (screenshots or recording)

### 3. Documentation

- [ ] README covers: business problem, architecture, how to run, demo
- [ ] Data lineage generated (e.g. `dbt docs generate`)
- [ ] Cost note: what would this cost in cloud at this scale?
- [ ] Access control documented

### 4. CI/CD

- [ ] Test suite runs automatically on PR (e.g. GitHub Actions)
- [ ] Quality checks run on schedule
- [ ] Deployment is reproducible from a fresh clone

### 5. Release Gate

Use `templates/release-gate.yaml` to document evidence:
- All tests passing
- Quality checks passing
- Review completed
- Documentation complete
- Cost analysis done

### 6. Output

- Production pipeline running on schedule
- `README.md` — Complete project documentation
- `docs/cost-analysis.md` — Cost implications
- Pipeline health dashboard

## Related skills

- `phases/phase-7-serving.md` — Serving layer guidance
- `phases/phase-8-orchestration.md` — Orchestration guidance
- `phases/phase-9-governance.md` — Governance and CI/CD
- `implementation/orchestration/airflow-patterns.md` — Airflow DAG patterns
- `templates/release-gate.yaml` — Release gate template
- `templates/backfill-plan.yaml` — Backfill plan for future maintenance
