"""Tests for the rule evaluation layer."""

from src.reliability.evaluator import evaluate_rules
from src.reliability.models import CheckType, Severity

ROWS = [
    {"customer_id": "C1", "email": "a@example.com", "age": "30", "plan": "pro"},
    {"customer_id": "C2", "email": "b@example.com", "age": "25", "plan": "basic"},
    {"customer_id": "C2", "email": "bad-email", "age": "-2", "plan": "starter"},
    {"customer_id": "C4", "email": "d@example.com", "age": "", "plan": "pro"},
]


def test_evaluator_aggregates_findings_from_configured_rules() -> None:
    report = evaluate_rules(ROWS, dataset_name="customers", source="test.csv")

    assert report.dataset.row_count == 4
    assert report.finding_count == 4
    assert {finding.check for finding in report.findings} == {
        CheckType.COMPLETENESS,
        CheckType.UNIQUENESS,
        CheckType.VALIDITY,
    }


def test_evaluator_returns_empty_findings_for_clean_data() -> None:
    rows = [
        {"customer_id": "C1", "email": "a@example.com", "age": "30", "plan": "pro"},
        {"customer_id": "C2", "email": "b@example.com", "age": "25", "plan": "basic"},
    ]
    report = evaluate_rules(rows, dataset_name="customers", source="clean.csv")

    assert report.findings == ()


def test_evaluator_rejects_unknown_rule_types() -> None:
    rows = [{"customer_id": "C1"}]

    try:
        evaluate_rules(
            rows,
            dataset_name="customers",
            source="test.csv",
            rules=({"id": "bad", "type": "unknown"},),
        )
    except ValueError as exc:
        assert "Unsupported reliability rule type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
