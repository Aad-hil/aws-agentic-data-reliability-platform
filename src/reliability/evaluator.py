"""Evaluate configured reliability rules against a dataset."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .checks import check_completeness, check_orders_validity, check_schema, check_uniqueness, check_validity
from .models import DatasetMetadata, ReliabilityFinding, ReliabilityReport
from .rules import QUALITY_RULES


def evaluate_rules(
    rows: Sequence[Mapping[str, Any]],
    *,
    dataset_name: str,
    source: str,
    rules: Sequence[Mapping[str, Any]] = QUALITY_RULES,
) -> ReliabilityReport:
    """Run configured deterministic rules and return a normalized report."""
    rows = list(rows)
    columns = tuple(rows[0].keys()) if rows else ()
    findings: list[ReliabilityFinding] = []

    for rule in rules:
        rule_type = rule["type"]
        if rule_type == "completeness":
            findings.extend(check_completeness(rows, rule["columns"]))
        elif rule_type == "uniqueness":
            findings.extend(check_uniqueness(rows, rule["column"]))
        elif rule_type == "validity":
            findings.extend(check_validity(rows))
        elif rule_type == "orders_validity":
            findings.extend(check_orders_validity(rows))
        elif rule_type == "schema":
            findings.extend(check_schema(rows, rule["columns"]))
        else:
            raise ValueError(f"Unsupported reliability rule type: {rule_type}")

    return ReliabilityReport(
        dataset=DatasetMetadata(
            name=dataset_name,
            source=source,
            row_count=len(rows),
            columns=columns,
        ),
        findings=tuple(findings),
    )
