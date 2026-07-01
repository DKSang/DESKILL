---
name: de-ingest
description: "Implement the Bronze/raw ingestion layer to pull data from a source into storage reliably. Use this skill when the user says 'write an ingestion script', 'fetch data from API', 'load raw data', 'implement Bronze layer', 'connect to [source]', 'how do I ingest from [API/database/file]', 'write a data loader', or has a source contract ready and needs working ingestion code. Also use when existing ingestion code has no retry logic, no metadata tagging, or no validation — help refactor it."
---

# Skill: Implement Bronze Ingestion

## Purpose

Move data from source to raw storage **reliably** — no transformation, no business logic, just extract and load. Each source gets its own script. Concerns are separated: one source failing should not block another.

## When to stop at this skill

Done when Bronze storage has real data, the script has retry/logging/validation, and `_loaded_at` + `_source` metadata tags are present on every record.

---

## Steps

### Step 1 — Read the source contract

Open `contracts/source-<name>.yaml`. From it, determine:
- **Endpoint / access method**
- **Auth type** → load from `.env`
- **Schema** → use for validation
- **Schedule** → determine incremental strategy (full/incremental)
- **Rate limit** → calculate sleep time between calls if needed

### Step 2 — Implement using the standard pattern

Every ingestion script must have **5 components**:

| Component | Reason |
|-----------|--------|
| **Retry with exponential backoff** | API transient failures are normal — no retry = fragile pipeline |
| **Schema validation** | Catch contract drift early — before bad data reaches downstream |
| **Metadata tagging** | `_loaded_at`, `_source` → downstream needs to know where and when data came from |
| **Partitioned output** | By date → enables incremental load, no full refresh every time |
| **Actionable logging** | Logs must be sufficient to debug without rerunning — record request params, response status, row count |

### Step 3 — Start small, validate, then scale

**Don't** run full scope immediately. Process:
1. Run with 1 entity / 1 day / 1 page
2. Verify output schema and content
3. Scale to full scope once logic is verified

### Step 4 — Verify Bronze output

After running, validate:
```python
# Quick sanity check
import duckdb
conn = duckdb.connect()
print(conn.sql("SELECT COUNT(*), MIN(_loaded_at), MAX(_loaded_at) FROM read_parquet('data/bronze/<source>/**/*.parquet')").df())
```

---

## Output

Create `ingestion/<source-name>/ingest.py`:

```python
"""
ingestion/<source-name>/ingest.py

Ingests data from <Source Name> into Bronze storage.
Contract: contracts/source-<name>.yaml
Schedule: <frequency from contract>
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("<source-name>-ingestion")

# ─── Config ──────────────────────────────────────────────────────────────────
API_KEY = os.getenv("<SOURCE>_API_KEY")
BASE_URL = "<api-base-url>"
BRONZE_PATH = Path("data/bronze/<source-name>")
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds — doubles each retry: 2s, 4s, 8s


# ─── Retry ───────────────────────────────────────────────────────────────────
def fetch_with_retry(url: str, params: dict = None, retries: int = MAX_RETRIES) -> Any:
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(
                url,
                headers={"Authorization": f"Bearer {API_KEY}"},
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            logger.info(f"Fetched {url} | status={resp.status_code} | attempt={attempt}")
            return resp.json()
        except requests.RequestException as e:
            if attempt == retries:
                logger.error(f"All {retries} retries failed for {url}: {e}")
                raise
            wait = BACKOFF_BASE ** attempt
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)


# ─── Validation ──────────────────────────────────────────────────────────────
REQUIRED_FIELDS = ["<field1>", "<field2>"]  # From contract schema

def validate_schema(records: list[dict], source: str) -> list[dict]:
    valid, invalid = [], []
    for record in records:
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            logger.warning(f"Record missing fields {missing}: {record}")
            invalid.append(record)
        else:
            valid.append(record)

    if invalid:
        dlq_path = BRONZE_PATH / "_dlq" / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        dlq_path.parent.mkdir(parents=True, exist_ok=True)
        dlq_path.write_text(json.dumps(invalid, default=str))
        logger.warning(f"Routed {len(invalid)} invalid records to DLQ: {dlq_path}")

    logger.info(f"Validation: {len(valid)} valid, {len(invalid)} invalid")
    return valid


# ─── Metadata tagging ────────────────────────────────────────────────────────
def tag_metadata(records: list[dict], source: str, params: dict = None) -> list[dict]:
    loaded_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            **record,
            "_loaded_at": loaded_at,
            "_source": source,
            "_ingest_params": json.dumps(params or {}),
        }
        for record in records
    ]


# ─── Storage ─────────────────────────────────────────────────────────────────
def write_bronze(records: list[dict], partition_date: str, source: str) -> Path:
    import json
    partition_path = BRONZE_PATH / partition_date
    partition_path.mkdir(parents=True, exist_ok=True)
    output_file = partition_path / f"{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    output_file.write_text(json.dumps(records, default=str))
    logger.info(f"Wrote {len(records)} records to {output_file}")
    return output_file


# ─── Main ────────────────────────────────────────────────────────────────────
def ingest(partition_date: str = None):
    if not partition_date:
        partition_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    logger.info(f"Starting ingestion | source=<source-name> | partition={partition_date}")

    # 1. Fetch
    params = {"date": partition_date}
    raw_data = fetch_with_retry(f"{BASE_URL}/<endpoint>", params=params)

    # 2. Normalize to list
    records = raw_data if isinstance(raw_data, list) else raw_data.get("results", [raw_data])
    logger.info(f"Fetched {len(records)} records")

    # 3. Validate
    valid_records = validate_schema(records, source="<source-name>")

    # 4. Tag metadata
    tagged = tag_metadata(valid_records, source="<source-name>", params=params)

    # 5. Write
    output_path = write_bronze(tagged, partition_date, source="<source-name>")

    logger.info(f"Ingestion complete | records={len(tagged)} | output={output_path}")
    return {"records": len(tagged), "output": str(output_path)}


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    result = ingest(date)
    print(result)
```

---

## DONE WHEN

- [ ] Script runs successfully — Bronze storage has real data
- [ ] Retry with exponential backoff implemented
- [ ] Schema validation implemented — invalid records go to DLQ, don't crash the run
- [ ] `_loaded_at` and `_source` present on every record
- [ ] Output partitioned by date
- [ ] Logging sufficient to debug without rerunning

---

## Feedback loop

If the actual response differs from the contract → **update the contract immediately** (`contracts/source-<name>.yaml`), don't just fix the code.

## Next Step

After all sources have been ingested → run `/transform` to build Silver and Gold models.

> Script template: `skills/ingest/scripts/ingestion_template.py`
> Reference: `skills/ingest/references/ingestion_patterns.md`
