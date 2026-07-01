# Ingestion Patterns Reference
# Read this when: designing ingestion strategy for a specific source type.
# Do NOT paste this entire file into SKILL.md — load on demand.

## 1. Pagination Patterns

### Offset Pagination
Most common for REST APIs returning list results.
```python
def fetch_all_pages(base_url: str, params: dict, page_size: int = 100) -> list:
    records = []
    offset = 0
    while True:
        resp = fetch_with_retry(base_url, {**params, "limit": page_size, "offset": offset})
        page = resp.get("results", [])
        records.extend(page)
        if len(page) < page_size:  # Last page
            break
        offset += page_size
        time.sleep(0.1)  # Polite delay
    return records
```

### Cursor Pagination
Used by APIs returning a `next_cursor` or `next_url` token.
```python
def fetch_all_cursor(base_url: str, params: dict) -> list:
    records = []
    next_url = base_url
    while next_url:
        resp = fetch_with_retry(next_url, params if next_url == base_url else {})
        records.extend(resp.get("results", []))
        next_url = resp.get("next")  # None if last page
    return records
```

### Date-Range Batching
For APIs that don't paginate but limit by date range.
```python
from datetime import date, timedelta

def fetch_date_range(start: date, end: date, batch_days: int = 30) -> list:
    """Chunk large date ranges to avoid API timeouts or size limits."""
    records = []
    cursor = start
    while cursor <= end:
        batch_end = min(cursor + timedelta(days=batch_days - 1), end)
        records.extend(fetch_with_retry(url, {"from": cursor, "to": batch_end}))
        cursor = batch_end + timedelta(days=1)
        time.sleep(1)  # Rate limit courtesy delay
    return records
```

---

## 2. Incremental vs Full Refresh

### Full Refresh
Re-fetches all data every run. Simple, always correct.
- Use when: Data is small (<100k rows), can change historically (corrections, updates)
- Risk: API cost scales with history depth; slow for large datasets

```python
# Full refresh: always fetch from origin
def ingest_full(partition_date: str) -> list:
    return fetch_with_retry(url, {"all": True})
```

### Incremental (Watermark)
Fetch only records newer than last successful run.
- Use when: Large dataset, append-only or append-dominant
- Risk: Missed records if source allows late-arriving updates

```python
def get_last_loaded_at(bronze_path: Path) -> str:
    """Find the most recent _loaded_at from existing Bronze partitions."""
    partitions = sorted(bronze_path.glob("*/"), reverse=True)
    for partition in partitions:
        files = list(partition.glob("*.json"))
        if files:
            records = json.loads(files[-1].read_text())
            if records:
                return max(r.get("_loaded_at", "") for r in records)
    return "1970-01-01T00:00:00+00:00"  # epoch if no history

def ingest_incremental(partition_date: str) -> list:
    last_loaded = get_last_loaded_at(BRONZE_PATH)
    return fetch_with_retry(url, {"since": last_loaded})
```

### Partition-based Incremental
Each date partition is self-contained — reprocess by overwriting the partition.
- Use when: Data is naturally time-partitioned (daily OHLC, daily logs)
- Safest incremental pattern — easy to backfill and reprocess

```python
def partition_exists(partition_date: str) -> bool:
    partition = BRONZE_PATH / partition_date
    return partition.exists() and any(partition.glob("*.json"))

def ingest_skip_if_exists(partition_date: str) -> dict:
    if partition_exists(partition_date):
        logger.info(f"Partition {partition_date} already exists — skipping")
        return {"skipped": True}
    return ingest(partition_date)
```

---

## 3. Storage Backends

### Local Filesystem (Development)
```python
# Write JSON (preserves raw structure)
Path(f"data/bronze/{source}/{date}/{ts}.json").write_text(
    json.dumps(records, default=str)
)

# Write Parquet (better for large volumes)
import pandas as pd
pd.DataFrame(records).to_parquet(
    f"data/bronze/{source}/{date}/{ts}.parquet",
    index=False
)
```

### MinIO / S3 (Production)
```python
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
)

def write_to_s3(records: list, bucket: str, key: str) -> None:
    body = json.dumps(records, default=str).encode()
    s3.put_object(Bucket=bucket, Key=key, Body=body)
    logger.info(f"Wrote {len(records)} records to s3://{bucket}/{key}")
```

---

## 4. Rate Limit Handling

### Polite Sleep (Fixed Delay)
```python
CALLS_PER_MINUTE = 60
SLEEP_BETWEEN_CALLS = 60 / CALLS_PER_MINUTE  # 1 second between calls

for entity in entities:
    data = fetch_with_retry(url, {"id": entity})
    process(data)
    time.sleep(SLEEP_BETWEEN_CALLS)
```

### Adaptive Rate Limiter
```python
import threading

class RateLimiter:
    def __init__(self, calls_per_second: float):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            elapsed = time.time() - self.last_call
            remaining = self.min_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
            self.last_call = time.time()

limiter = RateLimiter(calls_per_second=5)  # 5 calls/sec max

for entity in entities:
    limiter.wait()
    data = fetch_with_retry(url, {"id": entity})
```

---

## 5. Error Handling Decision Tree

```
API call fails
├── 400 Bad Request → Fix params, don't retry → raise
├── 401 Unauthorized → Check API key in .env → raise
├── 403 Forbidden → Check permissions / quota exhausted → raise
├── 404 Not Found → Entity doesn't exist → skip, log WARNING
├── 429 Rate Limited → Respect Retry-After header, sleep, retry
├── 500 Server Error → Retry with backoff (transient)
├── 503 Unavailable → Retry with longer backoff
└── Timeout → Retry with backoff, reduce timeout if persistent
```

---

## 6. Backfill Pattern

When running for historical dates (catching up after outage or new project):
```python
from datetime import date, timedelta

def backfill(start_date: str, end_date: str = None, skip_existing: bool = True):
    """Run ingestion for a range of dates."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date) if end_date else date.today()

    results = []
    cursor = start
    while cursor <= end:
        date_str = cursor.isoformat()
        if skip_existing and partition_exists(date_str):
            logger.info(f"Skipping {date_str} — partition exists")
        else:
            logger.info(f"Backfilling {date_str}")
            result = ingest(date_str)
            results.append(result)
            time.sleep(0.5)  # Polite delay between dates
        cursor += timedelta(days=1)

    logger.info(f"Backfill complete: {len(results)} partitions ingested")
    return results

# Usage:
# python ingest.py backfill 2024-01-01 2024-06-30
```
