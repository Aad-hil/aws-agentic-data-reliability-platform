"""Deterministic reliability checks for tabular datasets."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterable, Mapping

from .models import CheckType, ReliabilityFinding, Severity


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_PLANS = {"basic", "pro", "enterprise"}


def check_completeness(
    rows: Iterable[Mapping[str, Any]],
    required_columns: Iterable[str],
) -> list[ReliabilityFinding]:
    """Find missing or blank values in required columns."""
    rows = list(rows)
    findings: list[ReliabilityFinding] = []

    for column in required_columns:
        missing_rows = [
            index + 1
            for index, row in enumerate(rows)
            if row.get(column) is None or str(row.get(column)).strip() == ""
        ]
        if missing_rows:
            findings.append(
                ReliabilityFinding(
                    check=CheckType.COMPLETENESS,
                    severity=Severity.ERROR,
                    column=column,
                    description=f"{len(missing_rows)} required value(s) are missing.",
                    observed_value=len(missing_rows),
                    expected_value=0,
                    evidence={"row_numbers": missing_rows},
                )
            )
    return findings


def check_uniqueness(
    rows: Iterable[Mapping[str, Any]],
    key_column: str,
) -> list[ReliabilityFinding]:
    """Find duplicate values for a key column."""
    rows = list(rows)
    values = [row.get(key_column) for row in rows]
    counts = Counter(value for value in values if value not in (None, ""))
    duplicates = {value: count for value, count in counts.items() if count > 1}

    if not duplicates:
        return []

    return [
        ReliabilityFinding(
            check=CheckType.UNIQUENESS,
            severity=Severity.CRITICAL,
            column=key_column,
            description=f"{len(duplicates)} duplicate key value(s) detected.",
            observed_value=duplicates,
            expected_value="Each key value occurs once",
            evidence={"duplicate_values": duplicates},
        )
    ]


def check_validity(rows: Iterable[Mapping[str, Any]]) -> list[ReliabilityFinding]:
    """Find values that violate basic domain rules for the sample dataset."""
    rows = list(rows)
    findings: list[ReliabilityFinding] = []

    invalid_emails = [
        (index + 1, row.get("email"))
        for index, row in enumerate(rows)
        if row.get("email") and not EMAIL_PATTERN.match(str(row["email"]))
    ]
    if invalid_emails:
        findings.append(
            ReliabilityFinding(
                check=CheckType.VALIDITY,
                severity=Severity.ERROR,
                column="email",
                description=f"{len(invalid_emails)} email value(s) have an invalid format.",
                observed_value=[value for _, value in invalid_emails],
                expected_value="A valid email address",
                evidence={"row_numbers": [row for row, _ in invalid_emails]},
            )
        )

    invalid_ages = [
        (index + 1, row.get("age"))
        for index, row in enumerate(rows)
        if row.get("age") is not None and (not _is_number(row["age"]) or not 0 <= float(row["age"]) <= 120)
    ]
    if invalid_ages:
        findings.append(
            ReliabilityFinding(
                check=CheckType.VALIDITY,
                severity=Severity.ERROR,
                column="age",
                description=f"{len(invalid_ages)} age value(s) fall outside the allowed range 0-120.",
                observed_value=[value for _, value in invalid_ages],
                expected_value="0-120",
                evidence={"row_numbers": [row for row, _ in invalid_ages]},
            )
        )

    invalid_plans = [
        (index + 1, row.get("plan"))
        for index, row in enumerate(rows)
        if row.get("plan") not in ALLOWED_PLANS
    ]
    if invalid_plans:
        findings.append(
            ReliabilityFinding(
                check=CheckType.VALIDITY,
                severity=Severity.ERROR,
                column="plan",
                description=f"{len(invalid_plans)} plan value(s) are outside the allowed domain.",
                observed_value=[value for _, value in invalid_plans],
                expected_value=sorted(ALLOWED_PLANS),
                evidence={"row_numbers": [row for row, _ in invalid_plans]},
            )
        )

    return findings


def check_schema(
    rows: Iterable[Mapping[str, Any]],
    expected_columns: Iterable[str],
) -> list[ReliabilityFinding]:
    """Find missing or unexpected columns in the dataset."""
    rows = list(rows)
    expected = set(expected_columns)
    observed = set(rows[0].keys()) if rows else set()
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)

    findings: list[ReliabilityFinding] = []
    if missing:
        findings.append(
            ReliabilityFinding(
                check=CheckType.SCHEMA,
                severity=Severity.CRITICAL,
                description="Expected column(s) are missing from the dataset.",
                observed_value=sorted(observed),
                expected_value=sorted(expected),
                evidence={"missing_columns": missing},
            )
        )
    if unexpected:
        findings.append(
            ReliabilityFinding(
                check=CheckType.SCHEMA,
                severity=Severity.WARNING,
                description="Unexpected column(s) are present in the dataset.",
                observed_value=sorted(observed),
                expected_value=sorted(expected),
                evidence={"unexpected_columns": unexpected},
            )
        )
    return findings


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
