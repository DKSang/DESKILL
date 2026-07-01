# Test Templates Reference
# Read this when: writing test cases for a specific calculation type.
# Copy the relevant template and fill in your specific values.

## Template 1 — dbt schema tests (YAML)
# Use for: not_null, unique, accepted_values, relationships on every model

```yaml
# models/<model_name>.yml
version: 2

models:
  - name: <model_name>
    description: "<What this model represents>"
    columns:

      # Primary key: always test not_null + unique
      - name: <pk_column>
        description: "Surrogate primary key"
        tests:
          - not_null
          - unique

      # Foreign key: test relationships to dimension
      - name: <fk_column>
        tests:
          - not_null
          - relationships:
              to: ref('<dim_model>')
              field: <pk_in_dim>

      # Categorical: test accepted values
      - name: <category_column>
        tests:
          - accepted_values:
              values: ["<value1>", "<value2>", "<value3>"]

      # Numeric: test expression (positive prices, non-negative volume, etc.)
      - name: <numeric_column>
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "> 0"
              name: "<column>_must_be_positive"

      # Date: test freshness (row in last N days)
      - name: <date_column>
        tests:
          - dbt_utils.recency:
              datepart: day
              field: <date_column>
              interval: 2
```

---

## Template 2 — dbt logic test (SQL)
# Use for: window functions, percentage calculations, aggregations with known expected output.
# Pattern: provide known input → compute result → compare to expected → return rows that FAIL.
# Zero rows returned = test passes.

```sql
-- tests/test_<calculation_name>.sql
-- WHAT: Verify [describe the calculation]
-- INPUT: [describe the known input]
-- EXPECTED: [describe the expected output]

WITH known_input AS (
    SELECT
        '<entity_id>'   AS <key>,
        <value1>        AS <input_field_1>,
        <value2>        AS <input_field_2>,
        <expected>      AS expected_result
),

actual_calculation AS (
    SELECT
        <key>,
        -- Replicate the calculation from your model
        (<input_field_1> - <input_field_2>) / NULLIF(<input_field_2>, 0) * 100 AS actual_result,
        expected_result
    FROM known_input
),

failures AS (
    SELECT *
    FROM actual_calculation
    WHERE ABS(actual_result - expected_result) > 0.001  -- tolerance for float
       OR (actual_result IS NULL AND expected_result IS NOT NULL)
)

-- Test passes when this query returns 0 rows
SELECT * FROM failures
```

---

## Template 3 — pytest unit test (Python)
# Use for: pandas/PySpark transformation functions tested in isolation.

```python
# tests/test_<function_name>.py
"""
Tests for <module.function_name>.
Each test covers exactly one behaviour — no combining multiple assertions unless they're the same concern.
"""

import pandas as pd
import pytest
from <module> import <function_to_test>


class Test<FunctionName>:
    """Group related tests for <function_name>."""

    # ── Happy path ──────────────────────────────────────────────────────────
    def test_basic_case(self):
        """Standard input produces expected output."""
        input_df = pd.DataFrame({
            "<col1>": [<value1>],
            "<col2>": [<value2>],
        })
        result = <function_to_test>(input_df)
        assert result.iloc[0]["<output_col>"] == <expected_value>

    # ── Edge cases ──────────────────────────────────────────────────────────
    def test_empty_input_returns_empty(self):
        """Function does not crash on empty DataFrame — returns empty."""
        input_df = pd.DataFrame(columns=["<col1>", "<col2>"])
        result = <function_to_test>(input_df)
        assert len(result) == 0
        assert list(result.columns) == ["<expected_output_cols>"]

    def test_null_in_key_column(self):
        """Null in join/key column → record excluded (not crash)."""
        input_df = pd.DataFrame({
            "<key_col>": [None, "<valid_key>"],
            "<value_col>": [100, 200],
        })
        result = <function_to_test>(input_df)
        assert len(result) == 1  # null record excluded
        assert result.iloc[0]["<key_col>"] == "<valid_key>"

    def test_duplicate_keys_deduplicated(self):
        """Duplicate natural keys → keep only one record (latest by _loaded_at)."""
        input_df = pd.DataFrame({
            "<key_col>": ["<key>", "<key>"],
            "<value_col>": ["old", "new"],
            "_loaded_at": ["2024-01-01", "2024-01-02"],
        })
        result = <function_to_test>(input_df)
        assert len(result) == 1
        assert result.iloc[0]["<value_col>"] == "new"

    # ── Known input → known output (calculation verification) ───────────────
    def test_percentage_change_calculation(self):
        """(current - previous) / previous * 100 with known values."""
        input_df = pd.DataFrame({
            "current_close": [110.0],
            "prev_close": [100.0],
        })
        result = <function_to_test>(input_df)
        assert abs(result.iloc[0]["pct_change"] - 10.0) < 0.001

    def test_division_by_zero_returns_null(self):
        """When prev_close = 0, pct_change must be NULL (not infinity or error)."""
        input_df = pd.DataFrame({
            "current_close": [110.0],
            "prev_close": [0.0],
        })
        result = <function_to_test>(input_df)
        assert pd.isna(result.iloc[0]["pct_change"])
```

---

## Template 4 — Window function test (dbt SQL)
# Use for: rolling averages, lags, cumulative sums.
# Tests window boundaries — first/last record in window is the most error-prone.

```sql
-- tests/test_rolling_average.sql
-- WHAT: 7-day moving average of close price
-- EDGE CASE: First 6 days don't have full window — should use partial window

WITH input AS (
    -- 10 days of sequential prices for 1 ticker
    SELECT 'TEST' AS ticker, (SEQUENCE(1, 10)) AS day_nums
),

expanded AS (
    SELECT ticker, UNNEST(day_nums) AS day_num,
           day_num * 10.0 AS close  -- prices: 10, 20, 30, ..., 100
    FROM input
),

with_ma7 AS (
    SELECT *,
        AVG(close) OVER (
            PARTITION BY ticker
            ORDER BY day_num
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS close_ma7
    FROM expanded
),

expected AS (
    SELECT 1 AS day_num, 10.0 AS expected_ma7
    UNION ALL
    SELECT 4, (10+20+30+40) / 4.0    -- partial window, day 4
    UNION ALL
    SELECT 7, (10+20+30+40+50+60+70) / 7.0  -- first full 7-day window
),

failures AS (
    SELECT a.day_num, a.close_ma7, e.expected_ma7
    FROM with_ma7 a
    JOIN expected e ON a.day_num = e.day_num
    WHERE ABS(a.close_ma7 - e.expected_ma7) > 0.01
)

SELECT * FROM failures
```

---

## Template 5 — Integration test (dbt)
# Use for: verify that Silver → Gold joins produce expected row counts (no fan-out, no dropped records).

```sql
-- tests/test_no_fanout_silver_to_gold.sql
-- WHAT: Silver → Gold join must not inflate row count (no N:M join fan-out)

WITH silver_count AS (
    SELECT COUNT(DISTINCT <natural_key>) AS n
    FROM {{ ref('stg_<source>') }}
),

gold_count AS (
    SELECT COUNT(*) AS n
    FROM {{ ref('fct_<fact>') }}
    WHERE <filter_for_same_scope>
)

-- If gold has more rows than silver, there's a fan-out from a bad join
SELECT
    s.n AS silver_unique,
    g.n AS gold_rows,
    g.n - s.n AS excess_rows
FROM silver_count s, gold_count g
WHERE g.n > s.n  -- Return rows only if there IS a fan-out (test fails)
```
