---
name: de-project-roadmap
description: "End-to-end framework for planning and building a data engineering project — from business problem to production-ready pipeline. Use whenever the user is working on ANY data engineering project, pipeline, ETL/ELT system, data platform, or data warehouse — in any domain. Trigger on: 'build a data pipeline', 'DE portfolio project', 'data engineering project structure', 'where do I start with my DE project', 'roadmap for building X pipeline', 'plan my data engineering project', 'I have a business problem and need a data pipeline', or when the user is stuck mid-project and doesn't know what to do next. Skip only for pure data-analysis questions with no pipeline work involved."
---

# Data Engineering Project Roadmap

A domain-agnostic framework for building data engineering projects end-to-end — from business problem to production-ready pipeline. Each skill owns exactly **one deliverable**, guiding you step by step through the DE lifecycle.

## Core Principles

1. **Iterative, not linear** — phase boundaries are provisional; discoveries in later phases may require revisiting earlier ones. Always flag feedback loops.
2. **Undercurrents run throughout** — security, DataOps, data governance are not end-of-project checklists; raise them at each phase.
3. **Data contracts first** — document what you can rely on from each source *before* writing ingestion code.
4. **Testing ≠ Data Quality** — testing validates transformation *logic* at code-change time; DQ validates *actual data* at runtime.
5. **One tool per category** — commit to one choice rather than listing options "to compare later."

---

## Skill Flow — Suggested Order

Each skill produces one deliverable and then suggests the next skill to run. Follow the numbered sequence for a smooth end-to-end build.

```
   1. /problem    → docs/business_problem.md
         ↓
   2. /sources    → contracts/source-*.yaml (one per source)
         ↓
   3. /arch       → docs/architecture.md + data flow diagram
         ↓
   4. /schema     → docs/dw_schema.md (Fact/Dim + grain)
         ↓
   5. /env        → docker-compose.yml + .env.template + requirements.txt
         ↓
   6. /ingest     → ingestion/<source>/ingest.py (one per source)
         ↓
   7. /transform  → Silver + Gold models
         ↓
   8. /test       → test suite (schema + logic tests)
         ↓
   9. /dq         → runtime DQ checks (freshness, volume, drift)
         ↓
  10. /contract-check → validate actual data vs source contracts
         ↓
  11. /dag        → orchestration DAG (Airflow/Prefect/Dagster)
         ↓
  12. /serve      → serving layer (dashboard/API)
         ↓
  13. /ci         → CI/CD (GitHub Actions)
         ↓
  14. /docs       → README + data lineage + cost analysis
```

---

## Progress Checklist

```
STAGE 1 — DISCOVER
  [ ] docs/business_problem.md  →  /problem
  [ ] contracts/source-*.yaml   →  /sources

DESIGN
  [ ] docs/architecture.md      →  /arch
  [ ] docs/dw_schema.md         →  /schema
  [ ] docker-compose.yml        →  /env

BUILD
  [ ] ingestion/<source>/       →  /ingest
  [ ] Silver + Gold models      →  /transform
  [ ] tests/ all passing        →  /test

QUALITY
  [ ] quality/dq_checks.py      →  /dq
  [ ] contract_check_report.json→  /contract-check

SHIP
  [ ] dags/<project>_pipeline.py→  /dag
  [ ] serving/app.py            →  /serve
  [ ] .github/workflows/ci.yml  →  /ci
  [ ] README.md + cost_analysis →  /docs
```

---

## Skill Quick Reference

| Skill | Trigger | Output |
|-------|---------|--------|
| `/problem` | "I want to build a pipeline for..." | `docs/business_problem.md` |
| `/sources` | "What data sources should I use?" | `contracts/source-*.yaml` |
| `/arch` | "What architecture should I use?" | `docs/architecture.md` |
| `/schema` | "What tables should I create?" | `docs/dw_schema.md` |
| `/env` | "How do I set up my environment?" | `docker-compose.yml` |
| `/ingest` | "Write an ingestion script" | `ingestion/<source>/ingest.py` |
| `/transform` | "Transform my data / write dbt models" | Silver + Gold models |
| `/test` | "Write tests for my pipeline" | `tests/` all passing |
| `/dq` | "Check my data quality at runtime" | `quality/dq_checks.py` |
| `/contract-check` | "Validate data vs contracts" | Contract validation report |
| `/dag` | "Build my orchestration DAG" | `dags/<project>_pipeline.py` |
| `/serve` | "Build a dashboard / serving layer" | `serving/app.py` |
| `/ci` | "Set up CI for my pipeline" | `.github/workflows/ci.yml` |
| `/docs` | "Write my README / documentation" | `README.md` + lineage + cost |

---

## Code Patterns

For implementation-level patterns beyond what skills provide:

- `implementation/orchestration/` — Airflow DAG patterns
- `implementation/transformation/` — dbt model patterns
- `implementation/quality/` — Great Expectations, dbt tests
- `implementation/optimization/` — Spark partitioning, joins
- `implementation/pipeline/` — end-to-end pipeline patterns

## AI Time-Optimization Tips

- **AI fastest at**: boilerplate (Docker Compose, DAG skeletons, dbt scaffolding), summarizing API docs, generating test cases, writing docs
- **AI should not decide**: business-critical thresholds (what counts as anomaly), architecture tradeoffs, which DQ failures are acceptable to ship
- **Feedback loop check**: After each skill completes, ask "does this output change anything decided in an earlier skill?" — this single habit prevents silent rework accumulation
- **Verify AI-summarized API docs** against live source before building on them — training data can be stale
