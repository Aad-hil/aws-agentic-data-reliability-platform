"""AWS Lambda entry point for S3-backed agentic reliability analysis."""
from __future__ import annotations
import csv, io, json, logging, os, urllib.parse, uuid
from datetime import datetime, timezone
from typing import Any
import boto3
from src.agents.bedrock import BedrockClient
from src.agents.detection import DetectionAgent
from src.agents.rca import RCAAgent
from src.agents.recommendation import RecommendationAgent
from src.agents.orchestrator import ReliabilityOrchestrator
from src.reliability.evaluator import evaluate_rules
from src.reliability.profiler import profile_rows
from src.reliability.report import build_reliability_summary

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
s3 = boto3.client("s3")
REPORT_PREFIX = os.getenv("REPORT_PREFIX", "reports/")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")

def build_orchestrator() -> ReliabilityOrchestrator:
    if not BEDROCK_MODEL_ID:
        raise RuntimeError("BEDROCK_MODEL_ID must be configured")
    client = BedrockClient(model_id=BEDROCK_MODEL_ID)
    return ReliabilityOrchestrator(DetectionAgent(client), RCAAgent(client), RecommendationAgent(client))

def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    request_id = getattr(context, "aws_request_id", str(uuid.uuid4()))
    logger.info("Lambda invocation started", extra={"request_id": request_id, "record_count": len(event.get("Records", []))})
    processed: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    orchestrator = build_orchestrator()

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        if not key.startswith("input/") or not key.lower().endswith(".csv"):
            continue
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            rows = list(csv.DictReader(io.StringIO(response["Body"].read().decode("utf-8"))))
            dataset_name = key.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            source = f"s3://{bucket}/{key}"
            profile = profile_rows(rows, dataset_name=dataset_name, source=source)
            report = evaluate_rules(rows, dataset_name=dataset_name, source=source)
            summary = build_reliability_summary(report)
            workflow = orchestrator.run(reliability_report=summary, dataset_name=dataset_name,
                                        profile=profile, dataset_metadata=summary["dataset"])
            result = {"dataset": dataset_name, "reliability_report": summary,
                      "incident": workflow.incident, "rca": workflow.rca,
                      "recommendation": workflow.recommendation,
                      "processed_at": datetime.now(timezone.utc).isoformat(), "request_id": request_id}
            report_key = f"{REPORT_PREFIX.rstrip('/')}/{dataset_name}.json"
            s3.put_object(Bucket=bucket, Key=report_key,
                          Body=json.dumps(result, indent=2, default=str).encode("utf-8"),
                          ContentType="application/json")
            processed.append({"input_key": key, "report_key": report_key, "status": summary["status"]})
            logger.info("Dataset processed", extra={"request_id": request_id, "bucket": bucket, "key": key})
        except Exception as exc:
            logger.exception("Dataset processing failed", extra={"request_id": request_id, "bucket": bucket, "key": key})
            failures.append({"input_key": key, "error": exc.__class__.__name__})

    logger.info("Lambda invocation completed", extra={"request_id": request_id, "processed": len(processed), "failures": len(failures)})
    return {"processed": processed, "failures": failures}
