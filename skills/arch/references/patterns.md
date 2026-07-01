# Data Pipeline Architecture Patterns
# Read this when: choosing between ETL/ELT/Medallion/Lambda/Kappa/Lakehouse
# Do NOT paste this entire file into SKILL.md — load on demand.

## 1. Medallion Architecture (Bronze / Silver / Gold)

### What it is
Three-layer staging where each layer has a clear contract:
- **Bronze (Raw)**: Exact copy of source data, metadata-tagged. Never transformed, never deleted. Source of truth for recovery.
- **Silver (Cleaned)**: Deduplicated, typed, null-handled. No business logic. Joinable across sources.
- **Gold (Mart)**: Aggregated to business grain. Answers analytical questions directly. Optimized for query.

### When to choose
- Default for new DE projects
- Batch or micro-batch workloads (not stream-only)
- Want clear audit trail and reprocessing ability
- Portfolio projects — well understood by interviewers

### When NOT to choose
- Pure streaming (use Kappa)
- Very small data (<10k rows total) — overkill; just use Silver + Gold without Bronze

### Storage format recommendations
| Layer | Format | Reason |
|-------|--------|--------|
| Bronze | JSON or Parquet | JSON preserves original; Parquet for volume |
| Silver | Parquet (partitioned by date) | Columnar, efficient filter |
| Gold | Parquet or DuckDB table | Query engine can read either |

---

## 2. ELT (Extract → Load → Transform)

### What it is
Load raw data into the data warehouse first, then transform *inside* the warehouse using SQL.

### When to choose
- Cloud DW with abundant compute (Snowflake, BigQuery, Redshift)
- dbt as transformation layer (dbt runs SQL inside the warehouse)
- Want to preserve raw data in warehouse for ad-hoc querying
- Team is SQL-first

### Trade-offs
| Pro | Con |
|-----|-----|
| Simpler pipeline (no staging outside DW) | Cloud DW can get expensive at scale |
| All transformations in SQL — easy to debug | Compute costs tied to transform complexity |
| dbt integrates naturally | Less control over raw data format |

---

## 3. ETL (Extract → Transform → Load)

### What it is
Transform data *before* loading into the destination. Classic approach for legacy systems.

### When to choose
- Destination is a legacy system with strict schema requirements
- Heavy pre-processing needed (ML feature engineering, image/audio processing)
- PII must be masked before leaving source systems
- Data volume is enormous and transformation reduces size significantly

### When NOT to choose
- Modern cloud DW project — ELT is almost always better
- Small-to-medium data with no compliance constraint

---

## 4. Lambda Architecture

### What it is
Dual processing path: batch layer (accuracy) + speed layer (low latency) + serving layer (merges both).

### When to choose
- Need both: historical accuracy AND real-time updates
- Example: recommendation system needing historical model + real-time signals

### Warning
Lambda is complex to operate — two codebases for the same logic, must be kept in sync. Many teams regret choosing Lambda when Kappa would have sufficed.

---

## 5. Kappa Architecture

### What it is
Single stream processing path. Reprocessing is done by replaying the event log (Kafka offset reset).

### When to choose
- Stream-first: data arrives as events, not batches
- Kafka or Kinesis already in use
- Historical reprocessing can be done by replaying stream

### When NOT to choose
- Sources don't support event streaming (batch files, REST APIs)
- Team lacks streaming expertise

---

## 6. Lakehouse

### What it is
Combines data lake (cheap object storage) with data warehouse features (ACID transactions, schema enforcement, time travel) using open table formats.

**Open table formats**: Delta Lake, Apache Iceberg, Apache Hudi

### When to choose
- Need ACID transactions on object storage (S3/GCS/ADLS)
- Mix of batch and streaming workloads
- Need schema evolution without full rewrites
- Time travel / snapshot queries needed
- Scale: TB-PB range

### When NOT to choose
- Small-to-medium portfolio project — Delta/Iceberg has significant operational overhead
- Team unfamiliar with Spark ecosystem

---

## Tool Selection Guide

### Orchestration

| Tool | Choose when |
|------|------------|
| **Airflow** | Most common in job market; large community; best for complex DAG dependencies |
| **Dagster** | Asset-based model; excellent lineage; modern API; best for asset-heavy pipelines |
| **Prefect** | Modern Python API; easy local dev; good for smaller teams |
| **dbt (w/ Airflow)** | SQL transformation orchestration only; pair with Airflow for full pipeline |

**Default recommendation**: Airflow for portfolio projects (most recognizable on resume).

### Object Storage / Data Lake

| Tool | Choose when |
|------|------------|
| **MinIO** | Local/on-prem; S3-compatible; free; use for portfolio projects |
| **AWS S3** | Cloud production; cheapest at scale |
| **GCS** | Google ecosystem; pairs well with BigQuery |
| **ADLS** | Azure ecosystem; pairs with Synapse |

### Transformation

| Tool | Choose when |
|------|------------|
| **dbt Core** | SQL-first; version control for SQL; lineage docs; default for DW projects |
| **PySpark** | Distributed processing; >10GB data; complex transformations |
| **pandas/polars** | Single-machine; <5GB; Python-first; simplest to debug |
| **DuckDB** | Analytical queries on parquet files; no server needed; excellent for portfolio |

### Query Engine / Data Warehouse

| Tool | Choose when |
|------|------------|
| **DuckDB** | Local; free; excellent analytics performance; best for portfolio |
| **Snowflake** | Cloud; pay-per-use; excellent SQL; good if targeting Snowflake-heavy orgs |
| **BigQuery** | GCP; serverless; pay-per-query; good for GCP-focused orgs |
| **Redshift** | AWS; good integration with AWS ecosystem |

---

## Scale Decision Framework

Before choosing tools, estimate scale:

```
Daily volume (MB) = avg_record_size_KB × records_per_day / 1024

< 100 MB/day  → DuckDB + pandas/polars on single machine
100MB–10GB/day → DuckDB + dbt (still single machine, but think about partitioning)
> 10GB/day    → Consider Spark; move to distributed processing
> 100GB/day   → Cloud DW (Snowflake/BigQuery) or distributed Lakehouse
```

**Portfolio projects almost always fall in the <100MB/day bucket.** Don't optimize prematurely.
