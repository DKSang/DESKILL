#!/usr/bin/env python3
"""
validate_contract.py — Validate actual pipeline data vs source contracts.

Run after each ingestion to enforce contracts. Detects schema drift
(added/removed/renamed columns), type mismatches, and SLA freshness violations.

Usage:
    python quality/contract_check.py
    # or import: from quality.contract_check import validate_all_contracts

Contract path: contracts/source-*.yaml
Report path:   docs/contract_check_report.json
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
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
    """Get actual schema from the database. table_name must be a trusted identifier."""
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

    for col in expected_cols - actual_cols:
        violations.append(ContractViolation(
            source=source, check_type="missing_column",
            field=col, expected="exists", actual="missing", severity="error",
        ))

    for col in actual_cols - expected_cols:
        violations.append(ContractViolation(
            source=source, check_type="unexpected_column",
            field=col, expected="not in contract", actual="present", severity="warning",
        ))

    for col in expected_cols & actual_cols:
        expected_type = normalize_type(expected_props[col].get("type", "unknown"))
        actual_type = actual_schema[col]
        if expected_type not in actual_type and actual_type not in expected_type:
            violations.append(ContractViolation(
                source=source, check_type="type_mismatch",
                field=col, expected=expected_type, actual=actual_type, severity="error",
            ))

    return violations


def parse_freshness_hours(freshness_str: str) -> int | None:
    """Parse a SLA freshness string like '24h', '1d', '30m', '1.5h' → hours.

    Returns None if the string cannot be parsed.
    """
    if not freshness_str:
        return None
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(h|d|m)\s*$", freshness_str.strip().lower())
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2)
    return int(value * {"h": 1, "d": 24, "m": 1 / 60}[unit])


def _to_utc(ts) -> datetime:
    """Make a timestamp tz-aware (assume UTC if naive) for safe comparison."""
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(str(ts))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def check_freshness(contract: dict, conn, table: str, ts_col: str) -> list[ContractViolation]:
    """Check data freshness vs SLA. ts_col/table must be trusted identifiers."""
    violations = []
    source = contract["metadata"]["name"]
    hours = parse_freshness_hours(contract.get("sla", {}).get("freshness", ""))
    if hours is None:
        return violations

    row = conn.execute(f"SELECT MAX({ts_col}) FROM {table}").fetchone()
    latest = _to_utc(row[0])
    if latest is None:
        violations.append(ContractViolation(
            source=source, check_type="freshness",
            field=ts_col, expected=f"<= {contract['sla']['freshness']}",
            actual="NULL (no data)", severity="error",
        ))
        return violations

    age_hours = (datetime.now(timezone.utc) - latest).total_seconds() / 3600
    if age_hours > hours:
        violations.append(ContractViolation(
            source=source, check_type="freshness",
            field=ts_col, expected=f"<= {hours}h", actual=f"{age_hours:.1f}h", severity="error",
        ))
    return violations


def validate_all_contracts(conn, contracts_dir: str = "contracts",
                           table_mapping: dict | None = None,
                           report_path: str = "docs/contract_check_report.json") -> dict:
    contracts_path = Path(contracts_dir)
    all_violations: list[str] = []
    results: dict[str, Any] = {}

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

        violations = check_schema(contract, actual_schema)
        violations.extend(check_freshness(contract, conn, table, "_loaded_at"))

        for v in violations:
            (logger.error if v.severity == "error" else logger.warning)(str(v))
            all_violations.append(str(v))

        results[source_name] = {
            "status": "pass" if not any(v.severity == "error" for v in violations) else "fail",
            "violations": [str(v) for v in violations],
        }

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_violations": len(all_violations),
        "results": results,
    }
    out = Path(report_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    passed = sum(1 for r in results.values() if r.get("status") == "pass")
    failed = sum(1 for r in results.values() if r.get("status") == "fail")
    logger.info(f"Contract check complete: {passed} passed, {failed} failed")
    return report


if __name__ == "__main__":
    import duckdb
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    conn = duckdb.connect("data/warehouse.duckdb")
    print(json.dumps(validate_all_contracts(conn), indent=2))
