"""Tests for deterministic reliability checks."""

from src.reliability.checks import (
    check_completeness,
    check_schema,
    check_uniqueness,
    check_validity,
)
from src.reliability.models import CheckType, Severity


ROWS = [
    {"customer_id": "C1", "email": "a@example.com", "age": "30", "plan": "pro"},
    {"customer_id": "C2", "email": "b@example.com", "age": "25", "plan": "basic"},
    {"customer_id": "C2", "email": "bad-email", "age": "-2", "plan": "starter"},
    {"customer_id": "C4", "email": "d@example.com", "age": "", "plan": "pro"},
]


def test_completeness_finds_missing_values() -> None:
    findings = check_completeness(ROWS, ["customer_id", "email", "age"])
    assert len(findings) == 1
    assert findings[0].check == CheckType.COMPLETENESS
    assert findings[0].column == "age"
    assert findings[0].severity == Severity.ERROR


def test_uniqueness_finds_duplicate_keys() -> None:
    findings = check_uniqueness(ROWS, "customer_id")
    assert len(findings) == 1
    assert findings[0].check == CheckType.UNIQUENESS
    assert findings[0].severity == Severity.CRITICAL
    assert findings[0].evidence["duplicate_values"] == {"C2": 2}


def test_validity_finds_bad_email_age_and_plan() -> None:
    findings = check_validity(ROWS)
    assert {finding.column for finding in findings} == {"email", "age", "plan"}


def test_schema_passes_when_columns_match() -> None:
    findings = check_schema(ROWS, ["customer_id", "email", "age", "plan"])
    assert findings == []


def test_schema_finds_missing_and_unexpected_columns() -> None:
    findings = check_schema(ROWS, ["customer_id", "email", "age", "plan", "country"])
    assert len(findings) == 1
    assert findings[0].check == CheckType.SCHEMA
    assert findings[0].evidence["missing_columns"] == ["country"]
