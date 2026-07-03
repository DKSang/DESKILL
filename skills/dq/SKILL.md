---
name: de-dq
description: "Implement runtime data quality monitoring on actual pipeline output — freshness, volume, schema drift, and distribution checks. Use when the user asks 'check my data quality', 'set up DQ monitoring', 'freshness checks', 'volume anomaly detection', 'schema drift alerts', or 'monitor my pipeline data'. For testing transformation logic at code-change time, use /test."
---

# Skill: Data Quality Checks (Runtime)

## Purpose

Validate **actual data at runtime** — distinct from `/test`, which validates transformation **logic at code-change time**. Even correct code can produce bad data if a source changes, data lags, or upstream anomalies occur.

- **Testing** = "Does this SQL do what I think it does?"
- **DQ** = "Is today's data within expected bounds?"

## When to stop at this skill

Done when checks exist for freshness, volume, schema drift, and distribution — each threshold justified by domain knowledge or a documented source contract, not guesswork.

## Steps

### Step 1 — Identify the 4 required check types

| Type | Question | Threshold source |
|------|----------|-----------------|
| **Freshness** | Is the latest data within the SLA window? | `contracts/source-<name>.yaml` → `sla.freshness` |
| **Volume** | Is the row count within normal range? | Historical data: min/max from last 30 days |
| **Schema drift** | Did the source add/remove/rename fields? | `contracts/source-<name>.yaml` → schema |
| **Distribution** | Are values within a valid domain range? | Domain knowledge — not AI guesswork |

### Step 2 — Calibrate thresholds from domain knowledge

**Do not let AI set thresholds** — AI can suggest, but the user must verify and justify. For example:

- `volume_min`: Look at 30-day history, find the lowest day's record count. Subtract a 20% buffer.
- `price_range`: Can a stock price go to $0? Can it exceed $10,000? Domain knowledge.
- `freshness`: From contract SLA — if the source updates daily, freshness > 25h triggers alert.

### Step 3 — Write checks and alerts

Each check must:

- Return **clear pass/fail** (not just a log message).
- On fail → **alert immediately** (log level ERROR + notification).
- Record observed vs expected values for easy debugging.

## Output format

Create `quality/dq_checks.py`:

```python
"""
quality/dq_checks.py — Runtime data quality monitoring.

Run after each pipeline run to validate data output.
Each check: pass → log INFO; fail → log ERROR + alert.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Callable

logger = logging.getLogger("dq-checks")


# ─── Check framework ─────────────────────────────────────────────────────────

class DQResult:
    def __init__(self, check_name: str, passed: bool, observed: any,
                 expected: str, table: str, severity: str = "error"):
        self.check_name = check_name
        self.passed = passed
        self.observed = observed
        self.expected = expected
        self.table = table
        self.severity = severity
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def __repr__(self):
        status = "PASS" if self.passed else f"FAIL [{self.severity.upper()}]"
        return f"{status} | {self.table}.{self.check_name} | observed={self.observed} | expected={self.expected}"


def run_check(name: str, table: str, fn: Callable, expected_desc: str,
              severity: str = "error") -> DQResult:
    try:
        passed, observed = fn()
        result = DQResult(name, passed, observed, expected_desc, table, severity)
        if passed:
            logger.info(str(result))
        else:
            logger.error(str(result))
            send_alert(result)
        return result
    except Exception as e:
        logger.error(f"Check {name} raised exception: {e}")
        return DQResult(name, False, str(e), expected_desc, table, severity)


def send_alert(result: DQResult):
    """Send alert — customize with Slack webhook, email, etc."""
    # TODO: Replace with real notification (Slack, PagerDuty, etc.)
    logger.critical(f"DQ ALERT: {result}")


# ─── Freshness checks ─────────────────────────────────────────────────────────

def check_freshness(conn, table: str, timestamp_col: str, max_age_hours: int) -> DQResult:
    """Is the data within the SLA window?"""
    def _check():
        row = conn.sql(f"""
            SELECT MAX({timestamp_col}) AS latest
            FROM {table}
        """).fetchone()
        latest = row[0]
        if latest is None:
            return False, "NULL (no data)"
        age_hours = (datetime.now(timezone.utc) - latest).total_seconds() / 3600
        return age_hours <= max_age_hours, f"{age_hours:.1f}h ago"

    return run_check(
        name=f"freshness_{timestamp_col}",
        table=table,
        fn=_check,
        expected_desc=f"<= {max_age_hours}h",
        severity="error"
    )


# ─── Volume checks ────────────────────────────────────────────────────────────

def check_volume(conn, table: str, partition_col: str, partition_value: str,
                 min_rows: int, max_rows: int) -> DQResult:
    """Is the row count within normal range?"""
    def _check():
        row = conn.sql(f"""
            SELECT COUNT(*) FROM {table}
            WHERE {partition_col} = '{partition_value}'
        """).fetchone()
        count = row[0]
        return min_rows <= count <= max_rows, count

    return run_check(
        name=f"volume_{partition_value}",
        table=table,
        fn=_check,
        expected_desc=f"between {min_rows} and {max_rows}",
    )


# ─── Schema drift check ───────────────────────────────────────────────────────

def check_schema_drift(conn, table: str, expected_columns: list[str]) -> DQResult:
    """Has the source added/removed/renamed a column?"""
    def _check():
        actual_cols = {row[0] for row in conn.sql(f"DESCRIBE {table}").fetchall()}
        expected = set(expected_columns)
        added = actual_cols - expected
        removed = expected - actual_cols
        if added or removed:
            return False, f"added={list(added)}, removed={list(removed)}"
        return True, "no drift"

    return run_check(
        name="schema_drift",
        table=table,
        fn=_check,
        expected_desc=f"exactly {expected_columns}",
        severity="warning"
    )


# ─── Distribution checks ──────────────────────────────────────────────────────

def check_column_range(conn, table: str, column: str,
                       min_val: float, max_val: float) -> DQResult:
    """Are values within valid range?"""
    def _check():
        row = conn.sql(f"""
            SELECT
                MIN({column}) AS min_val,
                MAX({column}) AS max_val,
                COUNT(*) FILTER (WHERE {column} < {min_val} OR {column} > {max_val}) AS out_of_range
            FROM {table}
        """).fetchone()
        out_of_range = row[2]
        return out_of_range == 0, f"min={row[0]:.4f}, max={row[1]:.4f}, out_of_range={out_of_range}"

    return run_check(
        name=f"range_{column}",
        table=table,
        fn=_check,
        expected_desc=f"all values in [{min_val}, {max_val}]",
    )


# ─── Run all checks ───────────────────────────────────────────────────────────

def run_all_checks(conn, run_date: str = None) -> dict:
    if not run_date:
        run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    results = []

    # Freshness checks — thresholds from contracts/
    results.append(check_freshness(
        conn, table="fct_candles", timestamp_col="_loaded_at",
        max_age_hours=25  # Daily source → alert if >25h (25h = weekend buffer)
    ))

    # Volume checks — thresholds from historical data
    results.append(check_volume(
        conn, table="fct_candles",
        partition_col="trade_date", partition_value=run_date,
        min_rows=8000,   # NYSE+NASDAQ typically >9000 stocks, lowest day ~8000
        max_rows=12000,  # Upper cap to detect data duplication
    ))

    # Schema drift — from contract schema
    results.append(check_schema_drift(
        conn, table="fct_candles",
        expected_columns=["candle_id", "company_id", "time_id", "open", "high", "low", "close", "volume"]
    ))

    # Distribution — domain knowledge
    results.append(check_column_range(
        conn, table="fct_candles",
        column="close", min_val=0.01, max_val=100000  # Stock price: $0.01 - $100k
    ))

    # Summary
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    logger.info(f"DQ Summary: {passed} passed, {failed} failed")

    return {
        "run_date": run_date,
        "passed": passed,
        "failed": failed,
        "results": [str(r) for r in results],
    }


if __name__ == "__main__":
    import duckdb
    conn = duckdb.connect("data/warehouse.duckdb")
    results = run_all_checks(conn)
    print(json.dumps(results, indent=2))
```

## DONE WHEN

- [ ] Freshness check exists for every table with threshold from contract SLA
- [ ] Volume check exists with min/max from historical data (not arbitrary numbers)
- [ ] Schema drift check compares against contract schema
- [ ] Distribution check for important numeric columns with range from domain knowledge
- [ ] Every failed check → log ERROR and trigger alert
- [ ] `docs/dq_report.md` has check results with threshold rationale

## Next Step

Previous: `/test`. After done → run `/contract-check` to validate actual pipeline data against source contracts.

## References

- Template: `skills/dq/assets/dq_checks_template.md`
- Previous skill: `skills/test/SKILL.md`
- Next skill: `skills/contract-check/SKILL.md`
- Phase deep-dive: `phases/phase-6-data-quality.md`
- Quality patterns: `implementation/quality/data-quality-patterns.md`
