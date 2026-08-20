"""Orchestrate reliability checks into a single report."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .checks import check_completeness, check_schema, check_uniqueness, check_validity
from .models import DatasetMetadata, ReliabilityFinding, ReliabilityReport

EXPECTED_COLUMNS = (
    "customer_id",
    "full_name",
    "email",
    "signup_date",
    "country",
    "age",
    "plan",
    "monthly_spend",
)
REQUIRED_COLUMNS = EXPECTED_COLUMNS


def load_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load a CSV file into row dictionaries."""
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def run_reliability_checks(
    path: str | Path,
    *,
    dataset_name: str = "customer_dataset",
) -> ReliabilityReport:
    """Load a dataset, run all core checks, and return one normalized report."""
    rows = load_csv(path)
    columns = tuple(rows[0].keys()) if rows else tuple()

    findings: list[ReliabilityFinding] = []
    findings.extend(check_schema(rows, EXPECTED_COLUMNS))
    findings.extend(check_completeness(rows, REQUIRED_COLUMNS))
    findings.extend(check_uniqueness(rows, "customer_id"))
    findings.extend(check_validity(rows))

    metadata = DatasetMetadata(
        name=dataset_name,
        source=str(path),
        row_count=len(rows),
        columns=columns,
    )
    return ReliabilityReport(dataset=metadata, findings=tuple(findings))
