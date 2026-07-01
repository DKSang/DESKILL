# Transformation Patterns Reference
# Read this when: writing Silver or Gold model logic.
# Do NOT paste this entire file into SKILL.md — load on demand.

## Silver Layer Patterns

### 1. Deduplication — keep latest by natural key

**When**: Source sends duplicate records (duplicate API calls, redelivered events).
**Key insight**: Always deduplicate on the *natural business key*, not on ingestion order.

```sql
-- dbt: models/staging/stg_<source>.sql
WITH deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY <natural_key>           -- business key (ticker, order_id, user_id)
            ORDER BY _loaded_at DESC             -- keep the latest ingest
        ) AS _row_num
    FROM {{ source('<source>', 'raw') }}
)
SELECT * EXCLUDE (_row_num)
FROM deduplicated
WHERE _row_num = 1
```

```python
# pandas version
df = df.sort_values("_loaded_at", ascending=False)
df = df.drop_duplicates(subset=["<natural_key>"], keep="first")
```

---

### 2. Type Standardization

**Why**: Bronze stores everything as string/JSON; Silver must enforce correct types.
**Rule**: Cast explicitly — don't rely on implicit coercion.

```sql
SELECT
    -- Strings
    TRIM(UPPER(ticker))              AS ticker,           -- normalize casing
    NULLIF(TRIM(company_name), '')   AS company_name,     -- empty string → NULL

    -- Numeric
    CAST(close AS DECIMAL(12, 4))    AS close,
    CAST(volume AS BIGINT)           AS volume,

    -- Dates / Timestamps
    CAST(trade_date AS DATE)                        AS trade_date,
    CAST(timestamp AS TIMESTAMP WITH TIME ZONE)     AS event_at,

    -- Booleans
    CASE WHEN is_active = 'true' THEN TRUE
         WHEN is_active = 'false' THEN FALSE
         ELSE NULL END                              AS is_active,

    -- Metadata passthrough (always keep)
    _loaded_at,
    _source,
    _partition_date

FROM {{ source('<source>', 'raw') }}
```

---

### 3. Null Handling — explicit decisions, not silent drops

**Rule**: Every null-handling decision must be explicit and documented.
Never `WHERE field IS NOT NULL` without a comment explaining why.

```sql
SELECT
    -- Option 1: Use domain default
    COALESCE(sector, 'Unknown')     AS sector,

    -- Option 2: Flag as boolean (preserve the null signal)
    volume IS NOT NULL              AS has_volume,

    -- Option 3: Drop if critical field is null (document why)
    close  -- filtered below: records without close are not trading days

FROM silver_candles
WHERE close IS NOT NULL  -- Trading day definition: must have a closing price
```

---

### 4. Surrogate Key Generation

**Why**: Natural keys can be composite, long, or change (SCD). Surrogate keys give consistent int FK for joins.

```sql
-- dbt_utils
{{ dbt_utils.generate_surrogate_key(['ticker', 'trade_date']) }} AS candle_id

-- DuckDB / raw SQL
MD5(CONCAT(ticker, '|', trade_date::VARCHAR)) AS candle_id

-- Python
import hashlib
df["candle_id"] = df.apply(
    lambda r: hashlib.md5(f"{r.ticker}|{r.trade_date}".encode()).hexdigest(),
    axis=1
)
```

---

## Gold Layer Patterns

### 5. Aggregation at correct grain

**Rule**: Gold tables are defined by their grain. Every aggregation must produce exactly 1 row per grain combination.

```sql
-- Grain: 1 stock × 1 trading day
SELECT
    {{ dbt_utils.generate_surrogate_key(['ticker', 'trade_date']) }} AS candle_id,
    ticker,
    trade_date,
    -- Aggregates
    FIRST(open ORDER BY event_at)   AS open,
    MAX(high)                       AS high,
    MIN(low)                        AS low,
    LAST(close ORDER BY event_at)   AS close,
    SUM(volume)                     AS total_volume,
    COUNT(*)                        AS tick_count
FROM silver_ticks
GROUP BY ticker, trade_date
```

---

### 6. Window Functions — rolling metrics

**Common use cases**: moving averages, cumulative sums, period-over-period change.

```sql
WITH base AS (
    SELECT ticker, trade_date, close, volume
    FROM fct_candles
),

windowed AS (
    SELECT *,
        -- 7-day moving average
        AVG(close) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS close_ma7,

        -- 30-day moving average
        AVG(close) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS close_ma30,

        -- Previous close (lag 1 day)
        LAG(close, 1) OVER (PARTITION BY ticker ORDER BY trade_date) AS prev_close,

        -- Day-over-day % change
        -- Handle division by zero: prev_close = 0 → NULL
        CASE
            WHEN LAG(close, 1) OVER (PARTITION BY ticker ORDER BY trade_date) = 0 THEN NULL
            ELSE (close - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY trade_date))
                 / LAG(close, 1) OVER (PARTITION BY ticker ORDER BY trade_date) * 100
        END AS pct_change_1d
    FROM base
)

SELECT * FROM windowed
```

---

### 7. SCD Type 2 — Slowly Changing Dimensions

**Use when**: Dimension attributes change over time and history matters (company renamed, sector reclassified).

```sql
-- Initial load
INSERT INTO dim_companies
SELECT
    company_id,
    ticker,
    name,
    sector,
    CURRENT_DATE AS valid_from,
    NULL          AS valid_to,      -- NULL = currently active
    TRUE          AS is_current
FROM stg_companies;

-- Incremental update (when change detected)
-- 1. Close the old record
UPDATE dim_companies
SET valid_to    = CURRENT_DATE - INTERVAL '1 day',
    is_current  = FALSE
WHERE ticker = '<changed_ticker>'
  AND is_current = TRUE;

-- 2. Insert new record
INSERT INTO dim_companies (ticker, name, sector, valid_from, valid_to, is_current)
VALUES ('<changed_ticker>', '<new_name>', '<new_sector>', CURRENT_DATE, NULL, TRUE);
```

---

### 8. Incremental dbt Models

**`is_incremental()` pattern**: Only process new/changed records on subsequent runs.

```sql
{{
    config(
        materialized='incremental',
        unique_key='candle_id',          -- what defines "same record"
        on_schema_change='fail',         -- fail loudly if schema changes
        incremental_strategy='merge'     -- upsert: insert new + update changed
    )
}}

SELECT
    {{ dbt_utils.generate_surrogate_key(['ticker', 'trade_date']) }} AS candle_id,
    ticker,
    trade_date,
    close,
    volume
FROM {{ ref('stg_candles') }}

{% if is_incremental() %}
    -- Only process records newer than the last run
    WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}
```

---

## Performance Patterns

### 9. Partition Pruning

Always filter on the partition column first — before any joins or complex expressions.

```sql
-- GOOD: partition filter first → reads only relevant partitions
SELECT * FROM fct_candles
WHERE trade_date BETWEEN '2024-01-01' AND '2024-01-31'  -- partition prune
  AND ticker = 'AAPL';

-- BAD: function on partition column disables pruning
SELECT * FROM fct_candles
WHERE YEAR(trade_date) = 2024;  -- DuckDB/Spark can't prune on this
```

### 10. Join Order Optimization

Put the largest table (Fact) first; smaller tables (Dim) second.

```sql
-- GOOD: Fact first, Dims later
SELECT f.close, c.sector, t.quarter
FROM fct_candles f                        -- large (millions of rows)
JOIN dim_companies c ON f.ticker = c.ticker   -- small (thousands)
JOIN dim_time t ON f.trade_date = t.date      -- small (few thousand)

-- On very large Fact tables: use broadcast hint (Spark)
-- SELECT /*+ BROADCAST(c) */ f.close, c.sector
-- FROM fct_candles f JOIN dim_companies c ...
```
