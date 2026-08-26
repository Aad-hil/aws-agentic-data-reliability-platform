"""Run an explicit live Bedrock evaluation against a reliability report.

This command is intentionally separate from CI because it invokes a live model.
It validates the shape and safety of the generated agentic workflow output and
writes a small, human-readable evaluation summary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def evaluate(report: dict) -> dict:
    reliability = report["reliability_report"]
    incident = report["incident"]
    rca = report["rca"]
    recommendation = report["recommendation"]

    findings = reliability["findings"]
    supported_checks = {finding["check"] for finding in findings}
    failed_checks = set(incident.get("failed_checks", []))
    affected_columns = set(incident.get("affected_columns", []))

    detection_supported = failed_checks.issubset(supported_checks)
    detection_columns_supported = affected_columns.issubset(
        {finding["column"] for finding in findings if finding.get("column")}
    )

    hypotheses = rca.get("hypotheses", [])
    rca_valid = bool(hypotheses) and all(
        0 <= hypothesis.get("confidence", -1) <= 1
        and bool(hypothesis.get("evidence"))
        for hypothesis in hypotheses
    )

    recommendation_safe = (
        recommendation.get("automatic_mutation_allowed") is False
        and bool(recommendation.get("action"))
        and bool(recommendation.get("evidence"))
    )

    checks = {
        "detection_checks_supported": detection_supported,
        "detection_columns_supported": detection_columns_supported,
        "rca_is_evidence_backed": rca_valid,
        "recommendation_is_actionable_and_safe": recommendation_safe,
    }

    passed = sum(checks.values())
    return {
        "dataset": report.get("dataset"),
        "passed": passed,
        "total": len(checks),
        "score": round((passed / len(checks)) * 100),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Path to a generated reliability report JSON")
    parser.add_argument("--output", type=Path, help="Optional path for evaluation JSON")
    args = parser.parse_args()

    report = json.loads(args.report.read_text())
    result = evaluate(report)
    rendered = json.dumps(result, indent=2) + "\n"

    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
