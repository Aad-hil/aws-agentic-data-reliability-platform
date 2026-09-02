"""Transform reliability report JSON files into Tableau-ready CSV datasets.

The exporter is intentionally read-only: it consumes generated S3-report JSON
(or a local copy of it) and produces analytical extracts for Tableau/Athena.
It does not change reliability decisions or invoke AWS services.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


DATASET_RUN_FIELDS = (
    "run_id",
    "request_id",
    "dataset",
    "source",
    "processed_at",
    "row_count",
    "status",
    "quality_score",
    "finding_count",
    "info_count",
    "warning_count",
    "error_count",
    "critical_count",
)

FINDING_FIELDS = (
    "run_id",
    "dataset",
    "finding_id",
    "check_type",
    "severity",
    "column",
    "description",
    "observed_value",
    "expected_value",
    "affected_row_count",
    "affected_rows",
    "evidence",
)

AGENT_INSIGHT_FIELDS = (
    "run_id",
    "dataset",
    "incident_id",
    "priority",
    "issue_severity",
    "affected_columns",
    "hypothesis",
    "confidence",
    "uncertainty",
    "hypothesis_evidence",
    "recommendation",
    "recommendation_rationale",
    "recommendation_risk",
    "automatic_mutation_allowed",
)


def _json_value(value: Any) -> str:
    """Render nested values consistently for CSV consumption."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value)


def _text_evidence(value: Any) -> str:
    """Normalize model evidence without allowing character-by-character output."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if all(isinstance(item, dict) and set(item) == {"value"} for item in value):
            values = [item["value"] for item in value]
            if all(isinstance(item, str) and len(item) <= 1 for item in values):
                return "".join(values)
        if all(isinstance(item, str) for item in value):
            return " ".join(value)
    return _json_value(value)


def _run_id(report: dict[str, Any]) -> str:
    """Return a stable run identifier using the runtime request id when present."""
    request_id = report.get("request_id")
    if request_id:
        return str(request_id)
    raw = f"{report.get('dataset', '')}|{report.get('processed_at', '')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _finding_id(dataset: str, finding: dict[str, Any]) -> str:
    """Create a deterministic identifier for a finding."""
    raw = "|".join(
        str(finding.get(key, ""))
        for key in ("check", "severity", "column", "description")
    )
    digest = hashlib.sha256(f"{dataset}|{raw}".encode("utf-8")).hexdigest()[:12]
    return f"F-{digest}"


def _affected_rows(evidence: Any) -> tuple[int, str]:
    """Extract row-number evidence when the deterministic check provides it."""
    if isinstance(evidence, dict) and isinstance(evidence.get("row_numbers"), list):
        rows = evidence["row_numbers"]
        return len(rows), ",".join(str(row) for row in rows)
    return 0, ""


def transform_report(report: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Flatten one reliability report into the three analytical datasets."""
    reliability = report["reliability_report"]
    dataset_meta = reliability["dataset"]
    dataset = str(report.get("dataset") or dataset_meta.get("name") or "unknown")
    run_id = _run_id(report)
    counts = reliability.get("severity_counts", {})

    dataset_run = {
        "run_id": run_id,
        "request_id": str(report.get("request_id") or ""),
        "dataset": dataset,
        "source": str(dataset_meta.get("source") or ""),
        "processed_at": str(report.get("processed_at") or ""),
        "row_count": dataset_meta.get("row_count", 0),
        "status": reliability.get("status", ""),
        "quality_score": reliability.get("score", 0),
        "finding_count": reliability.get("finding_count", 0),
        "info_count": counts.get("info", 0),
        "warning_count": counts.get("warning", 0),
        "error_count": counts.get("error", 0),
        "critical_count": counts.get("critical", 0),
    }

    findings: list[dict[str, Any]] = []
    for finding in reliability.get("findings", []):
        row_count, rows = _affected_rows(finding.get("evidence"))
        findings.append(
            {
                "run_id": run_id,
                "dataset": dataset,
                "finding_id": _finding_id(dataset, finding),
                "check_type": finding.get("check", ""),
                "severity": finding.get("severity", ""),
                "column": finding.get("column", ""),
                "description": finding.get("description", ""),
                "observed_value": _json_value(finding.get("observed_value")),
                "expected_value": _json_value(finding.get("expected_value")),
                "affected_row_count": row_count,
                "affected_rows": rows,
                "evidence": _json_value(finding.get("evidence")),
            }
        )

    incident = report.get("incident") or {}
    rca = report.get("rca") or {}
    recommendation = report.get("recommendation") or {}
    hypotheses = rca.get("hypotheses") or []
    issue_severity = incident.get("severity", "")
    affected_columns = ",".join(str(value) for value in incident.get("affected_columns", []))
    recommendation_evidence = _text_evidence(recommendation.get("evidence"))

    insights: list[dict[str, Any]] = []
    for hypothesis in hypotheses:
        evidence = hypothesis.get("evidence", [])
        hypothesis_evidence = " | ".join(str(value) for value in evidence) if isinstance(evidence, list) else _text_evidence(evidence)
        insights.append(
            {
                "run_id": run_id,
                "dataset": dataset,
                "incident_id": incident.get("incident_id", ""),
                "priority": incident.get("priority", ""),
                "issue_severity": issue_severity,
                "affected_columns": affected_columns,
                "hypothesis": hypothesis.get("hypothesis", ""),
                "confidence": hypothesis.get("confidence", ""),
                "uncertainty": hypothesis.get("uncertainty", ""),
                "hypothesis_evidence": hypothesis_evidence,
                "recommendation": recommendation.get("action", ""),
                "recommendation_rationale": recommendation.get("rationale", ""),
                "recommendation_risk": recommendation.get("risk", ""),
                "automatic_mutation_allowed": recommendation.get("automatic_mutation_allowed", False),
            }
        )

    if insights and recommendation_evidence:
        # Keep the recommendation evidence available without creating another
        # grain in the model; it is represented in the rationale/evidence text.
        for row in insights:
            row["recommendation_rationale"] = (
                f"{row['recommendation_rationale']} Evidence: {recommendation_evidence}"
            ).strip()

    return dataset_run, findings, insights


def _write_csv(path: Path, fields: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def export_reports(reports_dir: Path, output_dir: Path) -> dict[str, int]:
    """Export all JSON reports in a directory."""
    reports = sorted(reports_dir.glob("*.json"))
    if not reports:
        raise FileNotFoundError(f"No JSON reports found in {reports_dir}")

    dataset_runs: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    insights: list[dict[str, Any]] = []

    for path in reports:
        with path.open(encoding="utf-8") as handle:
            report = json.load(handle)
        dataset_run, report_findings, report_insights = transform_report(report)
        dataset_runs.append(dataset_run)
        findings.extend(report_findings)
        insights.extend(report_insights)

    _write_csv(output_dir / "dataset_runs.csv", DATASET_RUN_FIELDS, dataset_runs)
    _write_csv(output_dir / "findings.csv", FINDING_FIELDS, findings)
    _write_csv(output_dir / "agent_insights.csv", AGENT_INSIGHT_FIELDS, insights)

    return {
        "reports": len(reports),
        "dataset_runs": len(dataset_runs),
        "findings": len(findings),
        "agent_insights": len(insights),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports_dir", type=Path, help="Directory containing generated report JSON files")
    parser.add_argument("output_dir", type=Path, help="Directory for Tableau-ready CSV files")
    args = parser.parse_args()

    counts = export_reports(args.reports_dir, args.output_dir)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
