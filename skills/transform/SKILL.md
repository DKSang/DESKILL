---
name: de-transform
description: "Implement Silver (cleaned) and Gold (analytics-ready) data transformation models for a data engineering project. Use this skill when the user says 'transform my data', 'write dbt models', 'write Spark jobs', 'clean raw data', 'build Silver layer', 'build Gold layer', 'implement transformation logic', 'deduplicate data', 'aggregate to grain', or has Bronze data and needs analytics-ready tables. Also use when the user asks how to go from raw data to something a dashboard can use."
---

# Skill: Implement Transformations (Silver + Gold)

## Purpose

Turn raw Bronze data into **Silver** (clean, trustworthy) and then **Gold** (analytics-ready, answering specific analytical questions). Every step is small and named clearly — so when numbers are wrong, you can trace back to the exact step that caused it.

## When to stop at this skill

Done when every Gold table answers at least 1 analytical question from `docs/business_problem.md` and all models run without errors.

---

## Steps

### Step 1 — Silver layer: clean Bronze

For each source, create a Silver model that does **4 things and only 4 things**:

| Task | Code pattern |
|------|-------------|
| **Standardize types** | Cast string dates → timestamp, string numbers → float |
| **Deduplicate** | By natural key (not ingestion order) |
| **Handle nulls explicitly** | Decide: default value / drop / flag — never use `DROP NULL` without documenting why |
| **Join sources** | Only join if both sources are clean, using join keys verified in the contract |

**DO NOT do in Silver**: business aggregations, derived metrics, business-rule filters.

### Step 2 — Gold layer: aggregations at the right grain

For each analytical question, create a Gold model at the **grain** defined in `docs/dw_schema.md`:

```sql
-- Gold: fct_candles_daily
-- Grain: 1 stock × 1 trading day
-- Answers: "daily OHLC and volume per stock"
SELECT
    {{ generate_surrogate_key(['company_id', 'trade_date']) }} AS candle_id,
    company_id,
    trade_date,
    open,
    high,
    low,
    close,
    volume
FROM {{ ref('stg_<source>') }}
WHERE close IS NOT NULL  -- Non-trading days → no record
```

### Step 3 — Incremental strategy

Choose the right strategy based on volume and update pattern:

| Strategy | When to use |
|----------|-------------|
| **Full refresh** | Small data (<1M rows), simpler. Use in dev. |
| **Incremental (append)** | Immutable events — only append new records |
| **Incremental (merge/upsert)** | Records may update — use a watermark column |
| **Incremental (delete+insert)** | When old records in a partition need to be replaced |

---

## Output by chosen tool

### If using dbt:

**Silver** (`models/staging/stg_<source>.sql`):
```sql
-- models/staging/stg_<source>.sql
{{
    config(
        materialized='incremental',
        unique_key='<natural_key>',
        on_schema_change='fail'
    )
}}

WITH source AS (
    SELECT * FROM {{ source('<source>', 'raw') }}
    {% if is_incremental() %}
    WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
    {% endif %}
),

renamed AS (
    SELECT
        CAST(<field1> AS VARCHAR)     AS <field1>,
        CAST(<field2> AS TIMESTAMP)   AS <field2_at>,
        CAST(<field3> AS DECIMAL(10,4)) AS <field3>,
        -- Deduplication: keep latest by natural key
        ROW_NUMBER() OVER (
            PARTITION BY <natural_key>
            ORDER BY _loaded_at DESC
        ) AS _row_num
    FROM source
)

SELECT * EXCEPT (_row_num)
FROM renamed
WHERE _row_num = 1
```

**Gold** (`models/marts/fct_<entity>_<grain>.sql`):
```sql
-- models/marts/fct_<entity>_<grain>.sql
{{
    config(
        materialized='table',
        post_hook="ANALYZE {{ this }}"
    )
}}

SELECT
    {{ dbt_utils.generate_surrogate_key(['<key1>', '<key2>']) }} AS <fact>_id,
    s.<key1>,
    t.time_id,
    s.<measure1>,
    s.<measure2>,
    -- Derived metrics (document the formula)
    CASE
        WHEN s.<measure1_prev> = 0 THEN NULL
        ELSE (s.<measure1> - s.<measure1_prev>) / s.<measure1_prev> * 100
    END AS pct_change
FROM {{ ref('stg_<source>') }} s
LEFT JOIN {{ ref('dim_time') }} t ON s.<date_field> = t.date
```

### If using Spark (PySpark):

```python
# transform/silver/<source>.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("silver-<source>").getOrCreate()

# Load Bronze
df = spark.read.json("data/bronze/<source>/**/*.json")

# Standardize types
df = df.withColumn("<date_field>", F.to_timestamp("<date_field>")) \
       .withColumn("<numeric_field>", F.col("<numeric_field>").cast("double"))

# Deduplicate
window = Window.partitionBy("<natural_key>").orderBy(F.desc("_loaded_at"))
df = df.withColumn("_row_num", F.row_number().over(window)) \
       .filter(F.col("_row_num") == 1) \
       .drop("_row_num")

# Handle nulls explicitly
df = df.withColumn("<field>",
    F.when(F.col("<field>").isNull(), F.lit(<default_value>))
     .otherwise(F.col("<field>"))
)

# Write Silver (Parquet, partitioned)
df.write.mode("overwrite").partitionBy("<date_col>") \
    .parquet("data/silver/<source>/")
```

---

## DONE WHEN

- [ ] Silver models: no duplicates by natural key, nulls handled explicitly, types standardized
- [ ] Gold models: created at the correct grain from `docs/dw_schema.md`
- [ ] Every analytical question from `docs/business_problem.md` has at least 1 Gold table answering it
- [ ] Incremental strategy is clear (full refresh / incremental) and documented
- [ ] Models run successfully without errors

---

## Next Step

After done → run `/test` to write a test suite for your transformation logic.

> Reference: `skills/transform/references/transformation_patterns.md`

