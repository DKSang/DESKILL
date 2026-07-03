---
name: de-transform
description: "Implement Silver (cleaned) and Gold (analytics-ready) data models. Trigger: 'transform my data', 'write dbt models', 'write Spark jobs', 'clean raw data', 'build Silver layer', 'build Gold layer', 'implement transformation logic', 'deduplicate data', 'aggregate to grain', or when the user has Bronze data and needs analytics-ready tables."
---

# Skill: Implement Transformations (Silver + Gold)

## Purpose

Turn raw Bronze data into **Silver** (clean, trustworthy) and then **Gold** (analytics-ready). Each step is small and named clearly so wrong numbers can be traced back to the step that produced them.

## When to stop at this skill

Done when every Gold table answers at least one analytical question from `docs/business_problem.md` and all models run without errors.

## Steps

### Step 1 â€” Silver layer: clean Bronze

For each source, create a Silver model that does **4 things and only 4 things**:

| Task | Code pattern |
|------|-------------|
| **Standardize types** | Cast string dates â†’ timestamp, string numbers â†’ float |
| **Deduplicate** | By natural key (not ingestion order) |
| **Handle nulls explicitly** | Default value / drop / flag â€” document the decision |
| **Join sources** | Only join if both sources are clean, using keys verified in the contract |

**Do NOT do in Silver**: business aggregations, derived metrics, business-rule filters.

### Step 2 â€” Gold layer: aggregations at the right grain

For each analytical question, create a Gold model at the grain defined in `docs/dw_schema.md`:

```sql
-- Gold: fct_candles_daily
-- Grain: 1 stock Ă— 1 trading day
-- Answers: "daily OHLC and volume per stock"
SELECT
    {{ dbt_utils.generate_surrogate_key(['company_id', 'trade_date']) }} AS candle_id,
    company_id,
    trade_date,
    open,
    high,
    low,
    close,
    volume
FROM {{ ref('stg_<source>') }}
WHERE close IS NOT NULL
```

### Step 3 â€” Incremental strategy

Choose the right strategy based on volume and update pattern:

| Strategy | When to use |
|----------|-------------|
| **Full refresh** | Small data (<1M rows), simpler. Use in dev. |
| **Incremental (append)** | Immutable events â€” only append new records |
| **Incremental (merge/upsert)** | Records may update â€” use a watermark column |
| **Incremental (delete+insert)** | Old records in a partition must be replaced |

## Output

### If using dbt

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
        CAST(<field2> AS TIMESTAMP)  AS <field2_at>,
        CAST(<field3> AS DECIMAL(10,4)) AS <field3>,
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
    CASE
        WHEN s.<measure1_prev> = 0 THEN NULL
        ELSE (s.<measure1> - s.<measure1_prev>) / s.<measure1_prev> * 100
    END AS pct_change
FROM {{ ref('stg_<source>') }} s
LEFT JOIN {{ ref('dim_time') }} t ON s.<date_field> = t.date
```

### If using Spark (PySpark)

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

# Write Silver
df.write.mode("overwrite").partitionBy("<date_col>") \
    .parquet("data/silver/<source>/")
```

## DONE WHEN

- [ ] Silver models: no duplicates by natural key, nulls handled explicitly, types standardized
- [ ] Gold models: created at the correct grain from `docs/dw_schema.md`
- [ ] Every analytical question from `docs/business_problem.md` has at least one Gold table answering it
- [ ] Incremental strategy is clear (full refresh / incremental) and documented
- [ ] Models run successfully without errors

## Next Step

Previous: `/ingest`. After done â†’ run `/test` to write a test suite for your transformation logic.

## References

- Transformation patterns: `skills/transform/references/transformation_patterns.md`
- Phase deep-dive: `phases/phase-5-transformation-testing.md`
- Previous skill: `skills/ingest/SKILL.md`
- Next skill: `skills/test/SKILL.md`
