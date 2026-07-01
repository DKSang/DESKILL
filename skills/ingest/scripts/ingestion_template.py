#!/usr/bin/env python3
"""
ingestion_template.py — Reusable ingestion script pattern.

Copy to: ingestion/<source-name>/ingest.py
Replace all <PLACEHOLDER> values before running.
Pattern: Extract → Validate schema → Tag metadata → Write partitioned Bronze.

Usage:
    python ingestion/<source>/ingest.py                  # today
    python ingestion/<source>/ingest.py 2024-01-15      # specific date
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

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("<SOURCE_NAME>-ingestion")

# ─── Config ───────────────────────────────────────────────────────────────────
# Load from .env — never hardcode credentials
API_KEY    = os.getenv("<SOURCE>_API_KEY")
API_SECRET = os.getenv("<SOURCE>_API_SECRET", "")  # if needed
BASE_URL   = "<https://api.example.com>"
SOURCE_NAME = "<source-name>"

# Bronze storage path (local) or S3 path (cloud)
# Local:  Path("data/bronze/<source-name>")
# S3:     "s3://bucket/bronze/<source-name>"
BRONZE_PATH = Path(f"data/bronze/{SOURCE_NAME}")

# Retry config — tune per source's reliability
MAX_RETRIES  = 3
BACKOFF_BASE = 2    # seconds — doubles each attempt: 2s, 4s, 8s
REQUEST_TIMEOUT = 30  # seconds

# Schema from contract (contracts/source-<name>.yaml → schema.properties)
# Only required fields — optional fields validated separately
REQUIRED_FIELDS = [
    "<field1>",
    "<field2>",
    # Add all required fields from contract
]


# ─── 1. Fetch with retry ──────────────────────────────────────────────────────

def fetch_with_retry(
    url: str,
    params: dict = None,
    headers: dict = None,
    retries: int = MAX_RETRIES,
) -> Any:
    """
    GET a URL with exponential backoff retry.

    Why retry? Transient network failures, API rate-limit 429s, and
    brief source downtime are normal in production. Without retry,
    a single transient failure kills the entire pipeline run.
    """
    default_headers = {"Authorization": f"Bearer {API_KEY}"}
    if headers:
        default_headers.update(headers)

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                headers=default_headers,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            # Raise for 4xx/5xx — caught below
            response.raise_for_status()

            logger.info(
                f"fetch OK | url={url} | status={response.status_code} "
                f"| attempt={attempt}/{retries}"
            )
            return response.json()

        except requests.HTTPError as e:
            # 429 Rate Limited — respect Retry-After header if present
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", BACKOFF_BASE ** attempt))
                logger.warning(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue

            # 4xx client error (bad request, auth) — don't retry
            if 400 <= response.status_code < 500:
                logger.error(f"Client error {response.status_code} — not retrying: {e}")
                raise

            # 5xx server error — retry
            if attempt == retries:
                logger.error(f"All {retries} retries failed: {e}")
                raise

        except requests.RequestException as e:
            if attempt == retries:
                logger.error(f"All {retries} retries failed: {e}")
                raise

        wait = BACKOFF_BASE ** attempt
        logger.warning(f"Attempt {attempt} failed. Retrying in {wait}s...")
        time.sleep(wait)


# ─── 2. Validate schema ───────────────────────────────────────────────────────

def validate_schema(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Separate valid records from invalid ones.

    Why validate here (Bronze)?
    - Catch contract drift before bad data contaminates Silver/Gold.
    - DLQ (Dead Letter Queue) preserves invalid records for debugging
      without crashing the entire pipeline run.
    - Required by `/contract-check` skill — invalid records are evidence of drift.
    """
    valid, invalid = [], []

    for record in records:
        missing = [f for f in REQUIRED_FIELDS if f not in record or record[f] is None]
        if missing:
            logger.warning(f"Record missing required fields {missing}: {str(record)[:100]}")
            invalid.append({**record, "_validation_error": f"missing: {missing}"})
        else:
            valid.append(record)

    logger.info(
        f"Validation | total={len(records)} valid={len(valid)} invalid={len(invalid)}"
    )
    return valid, invalid


def write_dlq(invalid_records: list[dict], partition_date: str) -> None:
    """Write invalid records to Dead Letter Queue partition."""
    if not invalid_records:
        return
    dlq_path = BRONZE_PATH / "_dlq" / partition_date
    dlq_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%H%M%S%f")
    out = dlq_path / f"{ts}.json"
    out.write_text(json.dumps(invalid_records, default=str))
    logger.warning(f"DLQ: wrote {len(invalid_records)} invalid records → {out}")


# ─── 3. Tag metadata ─────────────────────────────────────────────────────────

def tag_metadata(
    records: list[dict],
    partition_date: str,
    extra_params: dict = None,
) -> list[dict]:
    """
    Add standard Bronze metadata fields to every record.

    Why metadata tags?
    - `_loaded_at`: Silver/Gold use this for incremental loads and freshness checks.
    - `_source`: Required for data lineage — which source produced this record.
    - `_ingest_params`: Debug aid — what parameters produced this data.
    These fields must NOT be stripped in Silver; they flow through to Gold.
    """
    loaded_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            **record,
            "_loaded_at": loaded_at,
            "_source": SOURCE_NAME,
            "_partition_date": partition_date,
            "_ingest_params": json.dumps(extra_params or {}),
        }
        for record in records
    ]


# ─── 4. Write Bronze ─────────────────────────────────────────────────────────

def write_bronze(records: list[dict], partition_date: str) -> Path:
    """
    Write tagged records to Bronze partitioned by date.

    Partition by date because:
    - Enables incremental processing in downstream Silver — only reprocess new partitions.
    - Allows backfilling a specific date without touching others.
    - Consistent with how most DW tools (dbt, Spark, Hive) partition data.
    """
    partition_path = BRONZE_PATH / partition_date
    partition_path.mkdir(parents=True, exist_ok=True)

    # Timestamp in filename to support multiple runs per day (idempotent)
    ts = datetime.now(timezone.utc).strftime("%H%M%S")
    output_file = partition_path / f"{ts}.json"

    output_file.write_text(json.dumps(records, default=str, ensure_ascii=False))
    logger.info(f"Bronze write | path={output_file} | records={len(records)}")
    return output_file


# ─── 5. Main ingestion function ──────────────────────────────────────────────

def ingest(partition_date: str = None) -> dict:
    """
    Full ingestion run for one date partition.

    Args:
        partition_date: "YYYY-MM-DD" — defaults to today (UTC).

    Returns:
        dict with run statistics for DAG task logging.
    """
    if not partition_date:
        partition_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    logger.info(f"Ingestion start | source={SOURCE_NAME} | partition={partition_date}")

    # --- Step 1: Fetch ---
    # Adapt params to this source's API
    params = {
        "date": partition_date,
        # Add source-specific params from contract
    }
    raw = fetch_with_retry(f"{BASE_URL}/<endpoint>", params=params)

    # --- Step 2: Normalize to list ---
    # Most APIs return a list or wrap in a key — adapt here
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        records = raw.get("results", raw.get("data", raw.get("items", [raw])))
    else:
        raise ValueError(f"Unexpected response type: {type(raw)}")

    logger.info(f"Fetched {len(records)} records from API")

    # --- Step 3: Validate ---
    valid_records, invalid_records = validate_schema(records)
    write_dlq(invalid_records, partition_date)

    if not valid_records:
        logger.warning("No valid records after schema validation — check DLQ")
        return {"records": 0, "invalid": len(invalid_records), "output": None}

    # --- Step 4: Tag metadata ---
    tagged = tag_metadata(valid_records, partition_date, extra_params=params)

    # --- Step 5: Write Bronze ---
    output_path = write_bronze(tagged, partition_date)

    result = {
        "source": SOURCE_NAME,
        "partition_date": partition_date,
        "records": len(tagged),
        "invalid": len(invalid_records),
        "output": str(output_path),
    }
    logger.info(f"Ingestion complete | {result}")
    return result


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    result = ingest(partition_date=date_arg)
    print(json.dumps(result, indent=2))
