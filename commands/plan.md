---
description: "Design architecture, choose tooling, and set up environment"
---

# Data Engineering — Plan Command

Design the architecture and set up environment based on the spec. Run AFTER `/spec`.

## Instructions

### 1. Choose Architecture Pattern

| Pattern | When to Use |
|---------|-------------|
| **Medallion (Bronze/Silver/Gold)** | Default for most projects |
| **ELT** | Modern cloud DW, raw data preserved |
| **ETL** | Legacy systems, heavy pre-processing |
| **Kappa** | Stream-only, simplified pipeline |
| **Lakehouse** | Unified batch/stream, ACID on object store |

### 2. Pick One Tool Per Category

| Category | Options | Selection Criteria |
|----------|---------|-------------------|
| Orchestration | Airflow / Dagster / Prefect | Community size, job market |
| Transformation | dbt / Spark / pandas | Data volume, SQL vs code |
| Storage | MinIO / S3 / GCS / ADLS | Cloud vs local |
| Query engine | DuckDB / Snowflake / BigQuery | Scale, cost, portfolio value |
| Containerization | Docker Compose | Reproducibility |

### 3. Define Layer Contracts

For each Medallion layer, document:

- **Bronze**: Raw data as-is from source, with metadata (`_loaded_at`, `_source`)
- **Silver**: Cleaned, deduplicated, standardized types, validated schema
- **Gold**: Business-ready aggregations at the grain analytical questions need

### 4. Set Up Environment

- Write `docker-compose.yml` for chosen tools
- Init transformation project (e.g. `dbt init`)
- Create `.env` for secrets (excluded via `.gitignore`)
- Pin dependencies (`requirements.txt`)
- Verify `docker compose up` works from a fresh clone

### 5. Output

- `docs/architecture.md` — Architecture diagram + layer contracts
- `docker-compose.yml` — Reproducible environment
- Transformation project scaffold (e.g. dbt project)

### 6. Next Step

Run `/build` to implement ingestion and transformation.

## Related skills

- `phases/phase-2-architecture.md` — Detailed architecture methodology
- `phases/phase-3-environment-setup.md` — Environment setup guidance
- `implementation/pipeline/pipeline-patterns.md` — Architecture patterns
- `agents/data-engineer.md` — AI agent for architecture discussions
