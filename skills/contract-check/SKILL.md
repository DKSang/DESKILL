---
name: de-contract-check
description: "Validate actual pipeline output against source data contracts to detect schema drift, SLA violations, and field-level deviations. Use when the user asks 'validate my contracts', 'check schema drift', 'verify data matches contracts', 'contract compliance check', 'has my source schema changed', or 'detect breaking changes in my API'."
---

# Skill: Validate Data vs Contracts

## Purpose

Automatically verify that **actual running data** matches the **source contracts** (`contracts/*.yaml`). When a source changes schema or violates an SLA, detect it immediately — don't let the contract go stale while the code has already diverged.

- **Testing** (`/test`) = "Does transformation logic behave correctly?"
- **DQ** (`/dq`) = "Is today's data within expected bounds?"
- **Contract-check** (`/contract-check`) = "Does the actual data match the committed source contract?"

## When to stop at this skill

Done when every source contract is auto-verified after each ingestion run, and results are reported with clear pass/fail and specific diffs.

## Steps

### Step 1 — Load contracts

Read all `contracts/source-*.yaml`. Each contract has:

- `schema.properties` → expected fields + types
- `sla.freshness` → max allowed data age
- `quality.checks` → committed checks

### Step 2 — Compare against actual data

For each contract:

1. **Schema check**: Actual columns vs expected columns → detect added/removed/renamed
2. **Type check**: Actual types vs expected types
3. **Freshness check**: Latest `_loaded_at` vs SLA
4. **Quality checks**: Row count > 0, PK not null, etc.

### Step 3 — Report with clear diffs

A failure report must show **exactly** which fields differ and how — not just "contract violated."

## Output format

Create `quality/contract_check.py`:

```python
"""
quality/contract_check.py — Validate actual data vs source contracts.

Run after each ingestion to enforce contracts.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("contract-check")


@dataclass
class ContractViolation:
    source: str
    check_type: str
    field: str | None
    expected: Any
    actual: Any
    severity: str = "error"

    def __str__(self):
        field_str = f".{self.field}" if self.field else ""
        return (
            f"[{self.severity.upper()}] {self.source}{field_str} | "
            f"{self.check_type}: expected={self.expected}, actual={self.actual}"
        )


def load_contract(contract_path: Path) -> dict:
    with open(contract_path) as f:
        return yaml.safe_load(f)


def get_actual_schema(conn, table_name: str) -> dict[str, str]:
    """Get actual schema from the database."""
    rows = conn.execute(f"DESCRIBE {table_name}").fetchall()
    return {row[0]: row[1].upper() for row in rows}


def normalize_type(yaml_type: str) -> str:
    """Map YAML types → SQL types for comparison."""
    mapping = {
        "string": "VARCHAR",
        "integer": "INTEGER",
        "number": "DOUBLE",
        "boolean": "BOOLEAN",
        "datetime": "TIMESTAMP",
        "date": "DATE",
    }
    return mapping.get(yaml_type.lower(), yaml_type.upper())


def check_schema(contract: dict, actual_schema: dict) -> list[ContractViolation]:
    """Compare contract schema vs actual schema."""
    violations = []
    source = contract["metadata"]["name"]
    expected_props = contract.get("schema", {}).get("properties", {})

    expected_cols = set(expected_props.keys())
    actual_cols = set(actual_schema.keys())

    # Missing columns (breaking change)
    for col in expected_cols - actual_cols:
        violations.append(ContractViolation(
            source=source, check_type="missing_column",
            field=col, expected="exists", actual="missing", severity="error"
        ))

    # New columns (possible schema drift)
    for col in actual_cols - expected_cols:
        violations.append(ContractViolation(
            source=source, check_type="unexpected_column",
            field=col, expected="not in contract", actual="present", severity="warning"
        ))

    # Type mismatches
    for col in expected_cols & actual_cols:
        expected_type = normalize_type(expected_props[col].get("type", "unknown"))
        actual_type = actual_schema[col]
        if expected_type not in actual_type and actual_type not in expected_type:
            violations.append(ContractViolation(
                source=source, check_type="type_mismatch",
                field=col, expected=expected_type, actual=actual_type, severity="error"
            ))

    return violations


def check_freshness(contract: dict, conn, table: str, ts_col: str) -> list[ContractViolation]:
    """Check data freshness vs SLA."""
    from datetime import datetime, timezone
    violations = []
    source = contract["metadata"]["name"]
    sla = contract.get("sla", {})
    freshness_str = sla.get("freshness", "")

    if not freshness_str:
        return []

    hours = int(freshness_str.replace("h", "").replace("d", "")) * (
        24 if "d" in freshness_str else 1
    )

    row = conn.execute(f"SELECT MAX({ts_col}) FROM {table}").fetchone()
    latest = row[0]
    if latest is None:
        violations.append(ContractViolation(
            source=source, check_type="freshness",
            field=ts_col, expected=f"<= {freshness_str}", actual="NULL (no data)", severity="error"
        ))
        return violations

    age_hours = (datetime.now(timezone.utc) - latest).total_seconds() / 3600
    if age_hours > hours:
        violations.append(ContractViolation(
            source=source, check_type="freshness",
            field=ts_col, expected=f"<= {hours}h", actual=f"{age_hours:.1f}h", severity="error"
        ))

    return violations


def validate_all_contracts(conn, contracts_dir: str = "contracts",
                           table_mapping: dict = None) -> dict:
    contracts_path = Path(contracts_dir)
    all_violations = []
    results = {}

    for contract_file in contracts_path.glob("source-*.yaml"):
        contract = load_contract(contract_file)
        source_name = contract["metadata"]["name"]
        table = (table_mapping or {}).get(source_name, f"raw_{source_name.replace('-', '_')}")

        logger.info(f"Checking contract: {source_name} → {table}")

        try:
            actual_schema = get_actual_schema(conn, table)
        except Exception as e:
            logger.error(f"Cannot read table {table}: {e}")
            results[source_name] = {"status": "error", "message": str(e)}
            continue

        violations = []
        violations.extend(check_schema(contract, actual_schema))
        violations.extend(check_freshness(contract, conn, table, "_loaded_at"))

        for v in violations:
            if v.severity == "error":
                logger.error(str(v))
            else:
                logger.warning(str(v))
            all_violations.append(str(v))

        results[source_name] = {
            "status": "pass" if not any(v.severity == "error" for v in violations) else "fail",
            "violations": [str(v) for v in violations],
        }

    # Write report
    report = {
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "total_violations": len(all_violations),
        "results": results,
    }
    Path("docs/contract_check_report.json").write_text(json.dumps(report, indent=2))
    logger.info(f"Contract check complete: {sum(1 for r in results.values() if r['status'] == 'pass')} passed, "
                f"{sum(1 for r in results.values() if r['status'] == 'fail')} failed")
    return report


if __name__ == "__main__":
    import duckdb
    conn = duckdb.connect("data/warehouse.duckdb")
    report = validate_all_contracts(conn)
    print(json.dumps(report, indent=2))
```

## DONE WHEN

- [ ] Every `contracts/source-*.yaml` is auto-validated after each ingestion run
- [ ] Schema drift (added/removed/renamed columns) → detected and logged with diff
- [ ] Type mismatches → detected
- [ ] Freshness SLA violations → detected
- [ ] `docs/contract_check_report.json` generated after each run with clear pass/fail

## Next Step

Previous: `/dq`. After done → run `/dag` to wire everything into an orchestrated workflow.

## References

- Script: `skills/contract-check/scripts/validate_contract.py`
- Previous skill: `skills/dq/SKILL.md`
- Next skill: `skills/dag/SKILL.md`
- Phase deep-dives: `phases/phase-1-data-contracts.md`, `phases/phase-6-data-quality.md`
- Quality patterns: `implementation/quality/data-quality-patterns.md`
