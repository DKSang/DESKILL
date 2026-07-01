#!/usr/bin/env python3
"""
probe_source.py — Live-test một data source và in schema thực tế.

Dùng khi: cần lấy schema thực từ live call để điền vào source contract.
Không dùng docs API để làm schema — docs thường lạc hậu.

Usage:
  python probe_source.py --url "https://api.example.com/endpoint" \
                         --headers '{"Authorization": "Bearer TOKEN"}' \
                         --params '{"limit": 1}' \
                         --method GET
"""

import argparse
import json
import sys
import time
from typing import Any


def infer_type(value: Any) -> str:
    """Suy ra type từ giá trị thực."""
    if value is None:
        return "null (check if always nullable)"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        # Thử detect datetime
        import re
        datetime_patterns = [
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}",
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{8}T\d{6}",
        ]
        for pattern in datetime_patterns:
            if re.match(pattern, value):
                return "datetime"
        return "string"
    if isinstance(value, list):
        if value:
            inner_type = infer_type(value[0])
            return f"array of {inner_type}"
        return "array (empty — check real data)"
    if isinstance(value, dict):
        return "object"
    return str(type(value).__name__)


def flatten_schema(data: Any, prefix: str = "", depth: int = 0, max_depth: int = 3) -> list:
    """Flatten nested dict thành danh sách fields với type."""
    if depth > max_depth:
        return [{"field": prefix, "type": "object (max depth reached)", "sample": "..."}]

    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)) and depth < max_depth:
                results.extend(flatten_schema(value, full_key, depth + 1, max_depth))
            else:
                results.append({
                    "field": full_key,
                    "type": infer_type(value),
                    "sample": str(value)[:80] if value is not None else "null",
                    "nullable": value is None,
                })
    elif isinstance(data, list) and data:
        results.extend(flatten_schema(data[0], prefix, depth, max_depth))

    return results


def probe(url: str, method: str = "GET", headers: dict = None,
          params: dict = None, body: dict = None, timeout: int = 10) -> dict:
    """Gọi endpoint và trả về response + metadata."""
    try:
        import urllib.request
        import urllib.parse

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, method=method.upper())

        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        if body:
            req.data = json.dumps(body).encode()
            req.add_header("Content-Type", "application/json")

        start = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as response:
            elapsed = time.time() - start
            status = response.status
            raw = response.read().decode("utf-8")

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw_text": raw[:500]}

        return {
            "status": status,
            "elapsed_ms": round(elapsed * 1000),
            "data": data,
        }

    except Exception as e:
        return {"error": str(e), "data": None}


def main():
    parser = argparse.ArgumentParser(description="Probe a data source and print real schema")
    parser.add_argument("--url", required=True, help="Endpoint URL")
    parser.add_argument("--method", default="GET", help="HTTP method")
    parser.add_argument("--headers", default="{}", help="JSON string of headers")
    parser.add_argument("--params", default="{}", help="JSON string of query params")
    parser.add_argument("--body", default="{}", help="JSON string of request body")
    parser.add_argument("--max-depth", type=int, default=3, help="Max nesting depth to flatten")
    args = parser.parse_args()

    try:
        headers = json.loads(args.headers)
        params = json.loads(args.params)
        body = json.loads(args.body)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON argument — {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n🔍 Probing: {args.url}")
    print("─" * 60)

    result = probe(args.url, args.method, headers, params, body)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    print(f"✅ Status: {result['status']} | Latency: {result['elapsed_ms']}ms")
    print()

    data = result["data"]
    schema_fields = flatten_schema(data, max_depth=args.max_depth)

    print("📋 Schema (từ live response):")
    print("─" * 60)
    print(f"{'Field':<40} {'Type':<30} {'Sample'}")
    print(f"{'─'*40} {'─'*30} {'─'*30}")
    for field in schema_fields:
        print(f"{field['field']:<40} {field['type']:<30} {field.get('sample', '')}")

    print()
    print("📄 Raw sample (paste vào contract):")
    print("─" * 60)

    # In phần đầu response làm sample
    if isinstance(data, list):
        sample = data[0] if data else {}
    else:
        sample = data

    print(json.dumps(sample, indent=2, ensure_ascii=False)[:1000])

    print()
    print("📝 Copy vào contract:")
    print("─" * 60)
    print("schema:")
    print("  type: object")
    print("  properties:")
    for field in schema_fields:
        # Chỉ in top-level fields
        if "." not in field["field"]:
            print(f"    {field['field']}:")
            print(f"      type: {field['type']}")
            print(f"      description: \"\"")
            print(f"      required: {'false' if field.get('nullable') else 'true'}")
            print(f"      example: {repr(field.get('sample', ''))}")


if __name__ == "__main__":
    main()
