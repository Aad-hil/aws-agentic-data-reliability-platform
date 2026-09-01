"""Deterministic reliability checks for tabular datasets."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterable, Mapping

from .models import CheckType, ReliabilityFinding, Severity

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_PLANS = {"basic", "pro", "enterprise"}
ALLOWED_ORDER_PAYMENT_METHODS = {"card", "paypal", "bank_transfer", "cod", "upi"}
ALLOWED_ORDER_CHANNELS = {"web", "mobile", "store", "partner"}
ALLOWED_ORDER_STATUSES = {"pending", "paid", "processing", "shipped", "delivered", "cancelled", "refunded"}


def check_completeness(rows: Iterable[Mapping[str, Any]], required_columns: Iterable[str]) -> list[ReliabilityFinding]:
    """Find missing or blank values in required columns."""
    rows = list(rows)
    findings = []
    for column in required_columns:
        missing_rows = [i + 1 for i, row in enumerate(rows) if row.get(column) is None or str(row.get(column)).strip() == ""]
        if missing_rows:
            findings.append(ReliabilityFinding(
                check=CheckType.COMPLETENESS, severity=Severity.ERROR, column=column,
                description=f"{len(missing_rows)} required value(s) are missing.", observed_value=len(missing_rows),
                expected_value=0, evidence={"row_numbers": missing_rows},
            ))
    return findings


def check_uniqueness(rows: Iterable[Mapping[str, Any]], key_column: str) -> list[ReliabilityFinding]:
    """Find duplicate values for a key column."""
    values = [row.get(key_column) for row in rows]
    duplicates = {value: count for value, count in Counter(v for v in values if v not in (None, "")).items() if count > 1}
    if not duplicates:
        return []
    return [ReliabilityFinding(
        check=CheckType.UNIQUENESS, severity=Severity.CRITICAL, column=key_column,
        description=f"{len(duplicates)} duplicate key value(s) detected.", observed_value=duplicates,
        expected_value="Each key value occurs once", evidence={"duplicate_values": duplicates},
    )]


def check_validity(rows: Iterable[Mapping[str, Any]]) -> list[ReliabilityFinding]:
    """Find values that violate basic domain rules for the sample dataset."""
    rows = list(rows)
    findings = []

    invalid_emails = [(i + 1, row.get("email")) for i, row in enumerate(rows) if row.get("email") and not EMAIL_PATTERN.match(str(row["email"]))]
    if invalid_emails:
        findings.append(ReliabilityFinding(
            check=CheckType.VALIDITY, severity=Severity.ERROR, column="email",
            description=f"{len(invalid_emails)} email value(s) have an invalid format.",
            observed_value=[value for _, value in invalid_emails], expected_value="A valid email address",
            evidence={"row_numbers": [row for row, _ in invalid_emails]},
        ))

    invalid_ages = [(i + 1, row.get("age")) for i, row in enumerate(rows) if row.get("age") not in (None, "") and (not _is_number(row["age"]) or not 0 <= float(row["age"]) <= 120)]
    if invalid_ages:
        findings.append(ReliabilityFinding(
            check=CheckType.VALIDITY, severity=Severity.ERROR, column="age",
            description=f"{len(invalid_ages)} age value(s) fall outside the allowed range 0-120.", observed_value=[value for _, value in invalid_ages],
            expected_value="0-120", evidence={"row_numbers": [row for row, _ in invalid_ages]},
        ))

    invalid_plans = [(i + 1, row.get("plan")) for i, row in enumerate(rows) if row.get("plan") not in ALLOWED_PLANS]
    if invalid_plans:
        findings.append(ReliabilityFinding(
            check=CheckType.VALIDITY, severity=Severity.ERROR, column="plan",
            description=f"{len(invalid_plans)} plan value(s) are outside the allowed domain.", observed_value=[value for _, value in invalid_plans],
            expected_value=sorted(ALLOWED_PLANS), evidence={"row_numbers": [row for row, _ in invalid_plans]},
        ))
    return findings


def check_orders_validity(rows: Iterable[Mapping[str, Any]]) -> list[ReliabilityFinding]:
    """Find violations of the opt-in production orders domain rules."""
    rows = list(rows)
    findings: list[ReliabilityFinding] = []

    invalid_dates = [(i + 1, row.get("order_date")) for i, row in enumerate(rows) if not _is_iso_date(row.get("order_date"))]
    if invalid_dates:
        findings.append(ReliabilityFinding(
            check=CheckType.VALIDITY, severity=Severity.ERROR, column="order_date",
            description=f"{len(invalid_dates)} order date value(s) are invalid.", observed_value=[value for _, value in invalid_dates],
            expected_value="ISO date YYYY-MM-DD", evidence={"row_numbers": [row for row, _ in invalid_dates]},
        ))

    numeric_rules = (
        ("quantity", lambda value: _is_number(value) and float(value) > 0, "> 0"),
        ("unit_price", lambda value: _is_number(value) and float(value) >= 0, ">= 0"),
        ("discount_rate", lambda value: _is_number(value) and 0 <= float(value) <= 1, "0-1"),
        ("order_amount", lambda value: _is_number(value) and float(value) >= 0, ">= 0"),
    )
    for column, predicate, expected in numeric_rules:
        invalid = [(i + 1, row.get(column)) for i, row in enumerate(rows) if not predicate(row.get(column))]
        if invalid:
            findings.append(ReliabilityFinding(
                check=CheckType.VALIDITY, severity=Severity.ERROR, column=column,
                description=f"{len(invalid)} {column} value(s) are outside the allowed domain.",
                observed_value=[value for _, value in invalid], expected_value=expected,
                evidence={"row_numbers": [row for row, _ in invalid]},
            ))

    categorical_rules = (
        ("payment_method", ALLOWED_ORDER_PAYMENT_METHODS),
        ("channel", ALLOWED_ORDER_CHANNELS),
        ("status", ALLOWED_ORDER_STATUSES),
    )
    for column, allowed in categorical_rules:
        invalid = [(i + 1, row.get(column)) for i, row in enumerate(rows) if row.get(column) not in allowed]
        if invalid:
            findings.append(ReliabilityFinding(
                check=CheckType.VALIDITY, severity=Severity.ERROR, column=column,
                description=f"{len(invalid)} {column} value(s) are outside the allowed domain.",
                observed_value=[value for _, value in invalid], expected_value=sorted(allowed),
                evidence={"row_numbers": [row for row, _ in invalid]},
            ))
    return findings


def check_schema(rows: Iterable[Mapping[str, Any]], expected_columns: Iterable[str]) -> list[ReliabilityFinding]:
    """Find missing or unexpected columns in the dataset."""
    rows = list(rows)
    expected, observed = set(expected_columns), set(rows[0].keys()) if rows else set()
    missing, unexpected = sorted(expected - observed), sorted(observed - expected)
    findings = []
    if missing:
        findings.append(ReliabilityFinding(
            check=CheckType.SCHEMA, severity=Severity.CRITICAL,
            description="Expected column(s) are missing from the dataset.", observed_value=sorted(observed),
            expected_value=sorted(expected), evidence={"missing_columns": missing},
        ))
    if unexpected:
        findings.append(ReliabilityFinding(
            check=CheckType.SCHEMA, severity=Severity.WARNING,
            description="Unexpected column(s) are present in the dataset.", observed_value=sorted(observed),
            expected_value=sorted(expected), evidence={"unexpected_columns": unexpected},
        ))
    return findings


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _is_iso_date(value: Any) -> bool:
    if value is None:
        return False
    try:
        from datetime import date
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False
