---
description: "Implement ingestion, transformation, and data models"
---

# Data Engineering — Build Command

Build the data pipeline: ingest sources, transform to analytics-ready tables. Run AFTER `/plan`.

## Instructions

### 1. Implement Ingestion (Bronze Layer)

For each source (from `/spec` contracts):

- Write one ingestion script per source
- Start with a small subset to validate before scaling
- Add: retry with backoff, logging, metadata tags (`_loaded_at`, `_source`)
- Validate: status code, non-empty response, basic schema check
- Partition output for incremental loads (e.g. by date)

```python
# Pattern: batch ingestion with validation
def ingest_source(source_config):
    data = extract_with_retry(source_config)
    validated = validate_schema(data, source_config['schema'])
    write_to_bronze(validated, source_config['name'])
    log_metadata(source_config['name'], rows=len(validated))
```

### 2. Implement Transformations (Silver → Gold)

Using the chosen transformation tool (dbt/Spark/etc):

**Silver Layer** (cleaned):
- Standardize types
- Deduplicate by natural key
- Handle nulls explicitly
- Join sources on shared keys

**Gold Layer** (analytics-ready):
- Aggregate to the grain analytical questions need
- Compute derived metrics
- One table/view per analytical question from `/spec`

### 3. Add Tests

- Schema tests: not-null, uniqueness, accepted values on key columns
- Logic tests: known input → known expected output for non-trivial logic
- Run test suite after every change

### 4. Output

- Bronze storage populated with raw data
- Silver tables (cleaned, standardized)
- Gold tables (analytics-ready, answering spec questions)
- Passing test suite

### 5. Next Step

Run `/validate` to run data quality checks and verify pipeline.

## Related skills

- `phases/phase-4-ingestion.md` — Detailed ingestion guidance
- `phases/phase-5-transformation-testing.md` — Transformation + testing
- `implementation/transformation/dbt-patterns.md` — dbt code patterns
- `implementation/pipeline/pipeline-patterns.md` — Pipeline patterns
