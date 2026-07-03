---
name: de-test
description: "Write and run a data pipeline test suite covering schema and transformation logic. Trigger: 'write tests for my pipeline', 'test my transformations', 'add dbt tests', 'unit test my SQL', 'write schema tests', 'test my data models'. Note: this skill validates LOGIC at code-change time â€” for runtime data quality use /dq."
---

# Skill: Write & Run Test Suite

## Purpose

Prove that transformation **logic is correct** â€” not that data is correct (that's `/dq`). Tests run when code changes; DQ checks run when data changes.

- **Testing** = "Does this SQL do what I think it does?"
- **DQ** = "Is today's data within expected bounds?"

## When to stop at this skill

Done when schema tests and logic tests for every non-trivial calculation all pass.

## Steps

### Step 1 â€” Schema tests (required on every model)

Every Gold and Silver model must have at minimum:
- `not_null` on primary key
- `unique` on primary key
- `accepted_values` on categorical columns
- `relationships` for every FK â†’ Dim table

### Step 2 â€” Logic tests (required for non-trivial calculations)

"Non-trivial" = any calculation involving:
- Window functions (rolling average, cumulative sum, rank)
- Business rules with multiple conditions (complex CASE WHEN)
- Multi-source joins
- Percentage/ratio calculations

For each non-trivial calculation, write a test with **known input â†’ known expected output**. Verify AI-generated test cases manually â€” passing tests against incorrect code are worse than no tests.

### Step 3 â€” Edge cases to cover

| Edge case | Why it matters |
|-----------|---------------|
| Empty input | Model handles 0 records without crashing |
| Duplicate records | Silver dedup works correctly |
| Null in join key | Left join doesn't inflate or drop records |
| Out-of-order timestamps | Incremental logic doesn't miss records |
| First/last record in window | Window functions have correct boundaries |
| Division by zero | % change when previous = 0 |

## Output

### If using dbt

**Schema tests** (`models/<model>.yml`):

```yaml
version: 2

models:
  - name: fct_candles
    description: "Daily OHLC candles per stock"
    columns:
      - name: candle_id
        description: "Surrogate key"
        tests:
          - not_null
          - unique

      - name: company_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_companies')
              field: company_id

      - name: close
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "> 0"
              name: "close_price_positive"

  - name: stg_<source>
    columns:
      - name: <natural_key>
        tests:
          - not_null
          - unique
```

**Logic tests** (`tests/test_<calculation>.sql`):

```sql
-- tests/test_pct_change_calculation.sql
-- Verify: pct_change = (close - prev_close) / prev_close * 100
-- Known input: prev_close=100, close=110 â†’ expected pct_change=10.0

WITH input AS (
    SELECT
        'TEST001' AS ticker,
        100.0     AS prev_close,
        110.0     AS close,
        10.0      AS expected_pct_change
),

actual AS (
    SELECT
        ticker,
        (close - prev_close) / prev_close * 100 AS actual_pct_change,
        expected_pct_change
    FROM input
)

-- Test passes when this returns 0 rows
SELECT *
FROM actual
WHERE ABS(actual_pct_change - expected_pct_change) > 0.001
```

**Run tests:**

```bash
dbt test                        # All tests
dbt test --select fct_candles   # Single model
dbt test --store-failures       # Save failures to DB for inspection
```

### If using pytest + pandas/Spark

```python
# tests/test_silver_dedup.py
import pandas as pd
import pytest
from transform.silver.companies import deduplicate_companies


def test_dedup_keeps_latest_record():
    input_df = pd.DataFrame({
        "ticker": ["AAPL", "AAPL"],
        "name": ["Apple Old", "Apple New"],
        "_loaded_at": ["2024-01-01", "2024-01-02"],
    })
    result = deduplicate_companies(input_df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "Apple New"


def test_dedup_preserves_distinct_tickers():
    input_df = pd.DataFrame({
        "ticker": ["AAPL", "MSFT"],
        "name": ["Apple", "Microsoft"],
        "_loaded_at": ["2024-01-01", "2024-01-01"],
    })
    result = deduplicate_companies(input_df)
    assert len(result) == 2


def test_empty_input_returns_empty():
    input_df = pd.DataFrame(columns=["ticker", "name", "_loaded_at"])
    result = deduplicate_companies(input_df)
    assert len(result) == 0
```

**Run tests:**

```bash
pytest tests/ -v              # Run all
pytest tests/ -v --tb=short   # Short traceback on failure
```

## DONE WHEN

- [ ] Every Gold + Silver model has schema tests: `not_null`, `unique` on PK
- [ ] Every FK in Gold tables has a `relationships` test
- [ ] Every non-trivial calculation has a logic test with known input/output
- [ ] Edge cases covered: empty input, duplicates, nulls in join key
- [ ] All tests pass (`dbt test` or `pytest` returns 0 failures)

## Next Step

Previous: `/transform`. After done â†’ run `/dq` to implement runtime data quality monitoring.

## References

- Test templates: `skills/test/assets/test_templates.md`
- Phase deep-dive: `phases/phase-5-transformation-testing.md`
- Previous skill: `skills/transform/SKILL.md`
- Next skill: `skills/dq/SKILL.md`
