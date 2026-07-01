# DAG Patterns Reference
# Read this when: designing DAG structure, retry policy, or partial availability handling.
# Do NOT paste this entire file into SKILL.md — load on demand.

## 1. Dependency Patterns

### Fan-in (multiple ingestions → one transform)
```
ingest_A ──┐
ingest_B ──┼──► transform_silver ──► transform_gold ──► dq_checks
ingest_C ──┘
```
Implementation in Airflow:
```python
silver = transform_silver()
[ingest_a, ingest_b, ingest_c] >> silver
```

### Fan-out (one transform → multiple parallel tasks)
```
transform_gold ──┬──► dq_checks
                 └──► contract_check
```
```python
gold >> [dq_checks, contract_check]
```

### Source-level parallelism (same ingestion, multiple entities)
```python
from airflow.decorators import task_group

@task_group
def ingest_all_sources():
    tasks = []
    for source in ["source_a", "source_b", "source_c"]:
        @task(task_id=f"ingest_{source}")
        def _ingest(source_name=source):
            from ingestion import ingest
            return ingest(source_name)
        tasks.append(_ingest())
    return tasks
```

---

## 2. Retry Policy Guidelines

### By task type
```python
# Ingestion (API calls) — transient failures common
ingestion_retry_args = {
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(minutes=30),
}

# Transformation (dbt/Spark) — usually deterministic
transform_retry_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(hours=1),
}

# DQ Checks — rarely fails unless data is bad
dq_retry_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "execution_timeout": timedelta(minutes=15),
}
```

---

## 3. Schedule Strategy

### Match schedule to slowest critical source
```python
# If source A updates daily at midnight UTC:
schedule = "0 1 * * *"    # 1am UTC — 1h buffer for source propagation

# If source B updates hourly:
schedule = "15 * * * *"   # 15 min past every hour

# Multiple sources at different cadences → separate DAGs
# Fast sources: hourly sub-DAG
# Slow sources: daily main DAG
```

### Catchup strategy
```python
@dag(
    catchup=False,       # Don't backfill missed runs (safe default)
    max_active_runs=1,   # Prevent overlap if run takes longer than schedule
)
```

For intentional backfill, use Airflow's UI trigger with date range, or script:
```python
# Trigger backfill via CLI
# airflow dags backfill <dag_id> --start-date 2024-01-01 --end-date 2024-01-31
```

---

## 4. Partial Availability Handling

When some sources have data and others don't yet:

### Pattern A: Skip-and-log (recommended for non-critical sources)
```python
@task
def ingest_optional_source(ds):
    try:
        return ingest("optional_source", ds)
    except SourceUnavailableError as e:
        logger.warning(f"Optional source unavailable: {e} — skipping")
        return {"skipped": True, "records": 0}
```

### Pattern B: Short-circuit (stop DAG gracefully if critical source fails)
```python
from airflow.operators.python import ShortCircuitOperator

@task
def check_source_available(ds) -> bool:
    """Return False to skip all downstream tasks gracefully."""
    try:
        check_api_health(ds)
        return True
    except Exception:
        logger.warning("Critical source unavailable — short-circuiting DAG")
        return False

circuit = check_source_available()
circuit >> [ingest_a, ingest_b]  # Only runs if check returns True
```

### Pattern C: Wait with timeout (if source is usually just delayed)
```python
from airflow.sensors.http_sensor import HttpSensor

wait_for_source = HttpSensor(
    task_id="wait_for_source_api",
    http_conn_id="source_api",
    endpoint="/health",
    poke_interval=300,          # check every 5 minutes
    timeout=3600,               # fail after 1 hour of waiting
    mode="reschedule",          # release worker slot between pokes
)
```

---

## 5. Alerting Patterns

### Airflow — email on failure
```python
DEFAULT_ARGS = {
    "email_on_failure": True,
    "email_on_retry": False,
    "email": ["alerts@yourteam.com"],
}
```

### Airflow — Slack on failure
```python
def slack_alert(context):
    from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
    ti = context["task_instance"]
    SlackWebhookOperator(
        task_id="slack_alert",
        http_conn_id="slack_webhook",
        message=f"""
:red_circle: *Pipeline Failure*
*DAG*: {ti.dag_id}
*Task*: {ti.task_id}
*Run*: {context['ds']}
*Log*: {ti.log_url}
        """,
    ).execute(context)

@dag(on_failure_callback=slack_alert)
def pipeline(): ...
```

---

## 6. Idempotency — Safe to Re-run

Every task should be safe to re-run (same output if run twice).

```python
# GOOD: Idempotent — overwrites partition
def write_bronze_idempotent(records, partition_date):
    partition_path = BRONZE_PATH / partition_date
    # Remove existing files in partition before writing
    for f in partition_path.glob("*.json"):
        f.unlink()
    partition_path.mkdir(parents=True, exist_ok=True)
    (partition_path / "data.json").write_text(json.dumps(records))

# BAD: Not idempotent — appends on re-run → duplicates
def write_bronze_bad(records, partition_date):
    with open(BRONZE_PATH / partition_date / "data.json", "a") as f:
        f.write(json.dumps(records))  # ← appends every run!
```

---

## 7. Prefect vs Airflow Feature Comparison

| Feature | Airflow | Prefect |
|---------|---------|---------|
| DAG definition | Python decorators / operators | Python functions with `@flow`/`@task` |
| Local development | Docker required for full stack | `prefect server start` — simple |
| Dependency syntax | `task_a >> task_b` | `wait_for=[task_a]` in submit |
| Retry syntax | `retries=3` in `@task` | `retries=3` in `@task` |
| Scheduling | Cron in `@dag()` | `serve()` or deployment |
| Best for | Complex enterprise pipelines | Modern teams, simpler setup |
| Community | Very large; most Stack Overflow answers | Growing; excellent docs |
