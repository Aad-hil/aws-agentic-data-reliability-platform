"""Build a compact, machine-readable reliability report."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import ReliabilityReport, Severity

_SEVERITY_WEIGHTS = {
    Severity.INFO: 0,
    Severity.WARNING: 5,
    Severity.ERROR: 15,
    Severity.CRITICAL: 30,
}


def build_reliability_summary(report: ReliabilityReport) -> dict[str, Any]:
    """Convert findings into a stable summary suitable for JSON/auditing."""
    score = max(
        0,
        100 - sum(_SEVERITY_WEIGHTS[f.severity] for f in report.findings),
    )
    return {
        "dataset": asdict(report.dataset),
        "status": "failed" if report.findings else "passed",
        "score": score,
        "finding_count": report.finding_count,
        "severity_counts": {
            severity.value: sum(
                1 for finding in report.findings if finding.severity == severity
            )
            for severity in Severity
        },
        "findings": [
            {
                "check": finding.check.value,
                "severity": finding.severity.value,
                "column": finding.column,
                "description": finding.description,
                "observed_value": finding.observed_value,
                "expected_value": finding.expected_value,
                "evidence": finding.evidence,
            }
            for finding in report.findings
        ],
    }
