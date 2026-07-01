---
description: "Run data quality checks, validate contracts, verify pipeline"
---

# Data Engineering — Validate Command

Validate data quality and pipeline correctness. Run AFTER `/build`.

## Instructions

### 1. Data Quality Checks

| Dimension | Check | Tool |
|-----------|-------|------|
| Completeness | No missing values on key columns | GE / dbt test |
| Uniqueness | No duplicate primary keys | GE / dbt test |
| Freshness | Data arrived within expected window | dbt source freshness |
| Volume | Row count within expected range | GE / custom check |
| Schema drift | No unexpected column changes | GE / contract check |
| Distribution | Values within expected bounds | GE statistical checks |

### 2. Run Test Suite

```bash
# dbt
dbt build         # Run models + tests in DAG order
dbt test          # Run tests only

# Great Expectations
great_expectations checkpoint run <checkpoint_name>
```

### 3. Validate Contracts

Automatically verify pipeline output against source contracts:

- Each source's actual schema matches `contracts/<source>.yaml`
- Freshness SLA is met
- Row count expectations are satisfied
- No PII leaks in Gold layer

### 4. Generate Quality Report

Produce `docs/data-quality-report.md` with:
- Tables validated + pass/fail status
- Failed checks with observed values
- Freshness status per source
- Schema drift detected (if any)

### 5. Approval Gate

If all quality checks pass → proceed to `/review`.
If checks fail → diagnose and fix before proceeding.
Use `templates/release-gate.yaml` to document the validation evidence.

### 6. Next Step

Run `/review` for peer review of the pipeline.

## Related skills

- `phases/phase-6-data-quality.md` — Data quality methodology
- `implementation/quality/data-quality-patterns.md` — GE + dbt test patterns
- `templates/release-gate.yaml` — Release gate evidence template
