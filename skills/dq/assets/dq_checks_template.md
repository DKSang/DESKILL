# DQ Checks Template
# Copy to: docs/dq_checks_definition.md
# Document every check with threshold reasoning BEFORE implementing code.

## DQ Check Registry

### How to fill this template
For each check:
1. Decide the threshold from domain knowledge (not arbitrary numbers)
2. Document WHY that threshold (so future-you understands)
3. Decide severity: error (block pipeline) vs warning (alert but continue)

---

## Table: [table_name]

### CHECK-01: Freshness
| Field | Value |
|-------|-------|
| **Check** | Latest `_loaded_at` must be within SLA window |
| **Threshold** | ≤ [X] hours |
| **Threshold reasoning** | Source updates [daily/hourly]. Allow [Y]h buffer for pipeline processing time + weekends |
| **Severity** | error — stale data = incorrect dashboard numbers |
| **SQL** | `SELECT MAX(_loaded_at) FROM [table]; assert age_hours ≤ [X]` |

---

### CHECK-02: Volume (minimum)
| Field | Value |
|-------|-------|
| **Check** | Row count for today's partition ≥ min expected |
| **Threshold** | ≥ [min_rows] rows |
| **Threshold reasoning** | Historical data shows [entity type] has [N] records/day min. Took 30-day P5 (5th percentile) and subtracted 10% buffer. |
| **Severity** | error — below minimum suggests ingestion partial failure |
| **SQL** | `SELECT COUNT(*) FROM [table] WHERE partition_date = today; assert count ≥ [min]` |

---

### CHECK-03: Volume (maximum)
| Field | Value |
|-------|-------|
| **Check** | Row count ≤ max expected |
| **Threshold** | ≤ [max_rows] rows |
| **Threshold reasoning** | Historical P95 × 1.5. Exceeding this signals data duplication from double-run or source bug. |
| **Severity** | warning — could be legitimate expansion, needs investigation |
| **SQL** | `SELECT COUNT(*) FROM [table] WHERE partition_date = today; assert count ≤ [max]` |

---

### CHECK-04: PK not null
| Field | Value |
|-------|-------|
| **Check** | Primary key column has no nulls |
| **Threshold** | 0 nulls |
| **Threshold reasoning** | PK null = broken surrogate key generation or bad join. Zero tolerance. |
| **Severity** | error — null PK corrupts downstream joins |
| **SQL** | `SELECT COUNT(*) FROM [table] WHERE [pk_col] IS NULL; assert count = 0` |

---

### CHECK-05: PK uniqueness
| Field | Value |
|-------|-------|
| **Check** | No duplicate primary keys |
| **Threshold** | 0 duplicates |
| **Threshold reasoning** | Duplicates in Gold table = double-counting in aggregations. Zero tolerance. |
| **Severity** | error |
| **SQL** | `SELECT COUNT(*) - COUNT(DISTINCT [pk_col]) AS dupes FROM [table]; assert dupes = 0` |

---

### CHECK-06: Schema drift
| Field | Value |
|-------|-------|
| **Check** | Actual columns match expected columns from contract |
| **Expected columns** | [list from contracts/source-<name>.yaml → schema.properties] |
| **Threshold reasoning** | Column added by source = possible schema evolution; column removed = breaking change |
| **Severity** | added columns: warning (investigate); removed columns: error (pipeline broken) |

---

### CHECK-07: Numeric range
| Field | Value |
|-------|-------|
| **Check** | `[numeric_column]` values within valid domain range |
| **Range** | [min_val] ≤ value ≤ [max_val] |
| **Threshold reasoning** | [explain domain knowledge: "Stock prices can't be negative. Upper bound $100k covers Berkshire Hathaway's A share historically"] |
| **Out-of-range action** | Log WARNING with exact values; flag records; don't block pipeline |
| **Severity** | warning — may be legitimate outlier; needs investigation |

---

### CHECK-08: Null rate on important field
| Field | Value |
|-------|-------|
| **Check** | Null rate on `[important_column]` ≤ acceptable threshold |
| **Threshold** | ≤ [X]% nulls |
| **Threshold reasoning** | [Column] is null when [explain domain reason, e.g. "after-hours trades have no sector classification"]. Historical null rate is ~[Y]%; alert at 3×. |
| **Severity** | warning |

---

## Alert routing

| Severity | Action |
|----------|--------|
| **error** | Log ERROR → fail pipeline task → send Slack/email alert |
| **warning** | Log WARNING → continue pipeline → send Slack notification (non-blocking) |

## Escalation

If [N] or more checks fail in the same run → page on-call (or notify project owner) immediately, regardless of severity.
