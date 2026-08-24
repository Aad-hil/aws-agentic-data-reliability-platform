"""AWS Lambda entry point for S3-backed reliability analysis."""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime, timezone
from typing import Any

import boto3

from src.reliability.evaluator import evaluate_rules
from src.reliability.profiler import profile_rows
from src.reliability.report import build_reliability_summary

s3 = boto3.client("s3")
REPORT_PREFIX = os.getenv("REPORT_PREFIX", "reports/")


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Process S3 ObjectCreated events and persist a reliability report."""
    processed = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        if not key.startswith("input/"):
            continue

        response = s3.get_object(Bucket=bucket, Key=key)
        rows = list(csv.DictReader(io.StringIO(response["Body"].read().decode("utf-8"))))
        dataset_name = key.rsplit("/", 1)[-1].rsplit(".", 1)[0]

        profile = profile_rows(rows, dataset_name=dataset_name, source=f"s3://{bucket}/{key}")
        report = evaluate_rules(rows, dataset_name=dataset_name, source=f"s3://{bucket}/{key}")
        summary = build_reliability_summary(report)
        summary["profile"] = profile
        summary["processed_at"] = datetime.now(timezone.utc).isoformat()

        report_key = f"{REPORT_PREFIX.rstrip('/')}/{dataset_name}.json"
        s3.put_object(
            Bucket=bucket,
            Key=report_key,
            Body=json.dumps(summary, indent=2, default=str).encode("utf-8"),
            ContentType="application/json",
        )
        processed.append({"input_key": key, "report_key": report_key, "status": summary["status"]})

    return {"processed": processed}
