---
name: de-dag
description: "Build the orchestration DAG that wires ingestion, transformation, and quality tasks into a single scheduled workflow. Use when the user says 'build my DAG', 'orchestrate my pipeline', 'schedule my pipeline', 'connect all tasks', 'write Airflow DAG', 'set up Prefect/Dagster flow', or has individual tasks ready to wire into an end-to-end pipeline."
---

# Skill: Build Orchestration DAG

## Purpose

Connect all built tasks into **1 automated workflow** with explicit dependencies, retry policies, and scheduling aligned to source update frequency. A pipeline that fails without alerting is worse than having no pipeline at all.

## When to stop at this skill

Done when the full pipeline runs from a trigger, retry policies are in place, the schedule matches the slowest source update, and failures trigger alerts.

This skill follows `/dq` and `/contract-check`. Only move to `/serve` once the DAG runs end-to-end.

---

## Steps

### Step 1 — Map dependencies

Before writing the DAG, draw the dependency graph:
```
ingest_source_A ──┐
ingest_source_B ──┤─→ transform_silver ─→ transform_gold ─→ dq_checks ─→ contract_check
ingest_source_C ──┘
```

Rules:
- Transformation waits for **all** ingestion (or at least the sources it needs)
- Gold waits for Silver
- DQ checks wait for Gold
- Contract check runs alongside DQ checks

### Step 2 — Determine schedule

From `contracts/*.yaml` → take the slowest frequency of the most important source:
- If source is daily → schedule daily
- If source has intraday updates → may need a sub-DAG
- **Don't schedule faster than the source updates** → wasted compute

### Step 3 — Configure retry

| Task type | Retry | Delay | Timeout |
|-----------|-------|-------|---------|
| Ingestion (API call) | 3 | 5 min | 30 min |
| Transformation | 2 | 2 min | 60 min |
| DQ checks | 1 | 1 min | 15 min |

### Step 4 — Handle partial availability

When source A has data but source B doesn't: **skip-and-log, don't fail the entire DAG**. Pattern:
```python
# Airflow: short-circuit operator
# Prefect: conditional execution
# Dagster: asset partitioning
```

---

## Output

### If using Airflow — `dags/<project>_pipeline.py`:

```python
"""
dags/<project>_pipeline.py — Main pipeline DAG.

Schedule: <from contracts - slowest source>
Owner: <name>
"""

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
import logging

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "<owner>",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "email_on_failure": True,
    "email": ["<alert-email>"],
}


@dag(
    dag_id="<project>_pipeline",
    description="<project> data pipeline: ingest → transform → quality",
    schedule="0 1 * * *",  # Daily at 1am — adjust to source cadence
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["<domain>", "production"],
    doc_md="""
    ## <Project> Pipeline
    Ingests from <sources>, transforms to Silver/Gold, runs DQ checks.
    See docs/architecture.md for full design.
    """,
)
def pipeline():

    # ─── INGESTION ────────────────────────────────────────────────
    @task(task_id="ingest_<source_a>",
          execution_timeout=timedelta(minutes=30))
    def ingest_source_a(**context):
        run_date = context["ds"]
        from ingestion.source_a.ingest import ingest
        result = ingest(partition_date=run_date)
        logger.info(f"Ingested {result['records']} records from source_a")
        return result

    @task(task_id="ingest_<source_b>",
          execution_timeout=timedelta(minutes=30))
    def ingest_source_b(**context):
        run_date = context["ds"]
        from ingestion.source_b.ingest import ingest
        result = ingest(partition_date=run_date)
        logger.info(f"Ingested {result['records']} records from source_b")
        return result

    # ─── TRANSFORMATION ───────────────────────────────────────────
    @task(task_id="transform_silver",
          execution_timeout=timedelta(hours=1))
    def transform_silver(**context):
        run_date = context["ds"]
        import subprocess
        result = subprocess.run(
            ["dbt", "run", "--select", "staging.*",
             "--vars", f'{{"run_date": "{run_date}"}}'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise Exception(f"dbt staging failed:\n{result.stderr}")
        logger.info("Silver transformation complete")

    @task(task_id="transform_gold",
          execution_timeout=timedelta(hours=1))
    def transform_gold(**context):
        run_date = context["ds"]
        import subprocess
        result = subprocess.run(
            ["dbt", "run", "--select", "marts.*",
             "--vars", f'{{"run_date": "{run_date}"}}'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise Exception(f"dbt marts failed:\n{result.stderr}")
        logger.info("Gold transformation complete")

    # ─── QUALITY ──────────────────────────────────────────────────
    @task(task_id="dq_checks",
          execution_timeout=timedelta(minutes=15))
    def run_dq_checks(**context):
        run_date = context["ds"]
        import duckdb
        from quality.dq_checks import run_all_checks
        conn = duckdb.connect("data/warehouse.duckdb")
        results = run_all_checks(conn, run_date)
        if results["failed"] > 0:
            raise Exception(f"DQ checks failed: {results['failed']} failures. See docs/dq_report.md")
        return results

    @task(task_id="contract_check",
          execution_timeout=timedelta(minutes=15))
    def run_contract_check(**context):
        import duckdb
        from quality.contract_check import validate_all_contracts
        conn = duckdb.connect("data/warehouse.duckdb")
        report = validate_all_contracts(conn)
        failed = sum(1 for r in report["results"].values() if r["status"] == "fail")
        if failed > 0:
            raise Exception(f"Contract violations detected: {failed} sources failed")
        return report

    # ─── DEPENDENCY WIRING ────────────────────────────────────────
    ingest_a = ingest_source_a()
    ingest_b = ingest_source_b()

    silver = transform_silver()
    [ingest_a, ingest_b] >> silver

    gold = transform_gold()
    silver >> gold

    dq = run_dq_checks()
    contract = run_contract_check()
    gold >> [dq, contract]


pipeline_dag = pipeline()
```

### If using Prefect — `flows/<project>_pipeline.py`:

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(retries=3, retry_delay_seconds=300, cache_key_fn=task_input_hash,
      cache_expiration=timedelta(days=1))
def ingest_source_a(run_date: str): ...

@task(retries=2, retry_delay_seconds=120)
def transform_silver(run_date: str): ...

@flow(name="<project>-pipeline", log_prints=True)
def pipeline(run_date: str = None):
    import datetime
    if not run_date:
        run_date = datetime.date.today().isoformat()

    a = ingest_source_a.submit(run_date)
    b = ingest_source_b.submit(run_date)

    silver = transform_silver.submit(run_date, wait_for=[a, b])
    gold = transform_gold.submit(run_date, wait_for=[silver])

    dq_checks.submit(run_date, wait_for=[gold])
    contract_check.submit(run_date, wait_for=[gold])
```

---

## DONE WHEN

- [ ] All tasks are in the DAG with explicit dependencies (no implicit timing)
- [ ] Retry policy on every task (not just ingestion)
- [ ] Schedule matches the update frequency of the slowest important source
- [ ] Failure → alert (email / Slack / log ERROR)
- [ ] Full pipeline runs successfully from a manual trigger
- [ ] Partial availability handled (skip-and-log, don't fail the entire DAG)

---

## Next Step

Previous: `/dq` and `/contract-check`.

After done → run `/serve` to build the serving layer (dashboard/API).

If scheduling reveals a source cadence that conflicts with the contract or architecture, revisit `/sources` or `/arch` rather than patching the DAG silently.

---

## References

- Phase deep-dive: `phases/phase-8-orchestration.md`
- Orchestration patterns: `implementation/orchestration/airflow-patterns.md`
- Pipeline patterns: `implementation/pipeline/pipeline-patterns.md`
- Local reference: `skills/dag/references/dag_patterns.md`
