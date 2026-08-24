"""Tests for reliability report generation."""

from src.reliability.evaluator import evaluate_rules
from src.reliability.report import build_reliability_summary

ROWS = [
    {"customer_id": "C1", "email": "a@example.com", "age": "30", "plan": "pro"},
    {"customer_id": "C2", "email": "b@example.com", "age": "25", "plan": "basic"},
    {"customer_id": "C2", "email": "bad-email", "age": "-2", "plan": "starter"},
    {"customer_id": "C4", "email": "d@example.com", "age": "", "plan": "pro"},
]


def test_report_summarizes_failures_and_score() -> None:
    report = evaluate_rules(ROWS, dataset_name="customers", source="test.csv")
    summary = build_reliability_summary(report)

    assert summary["status"] == "failed"
    assert summary["finding_count"] == 4
    assert summary["severity_counts"]["critical"] == 1
    assert summary["severity_counts"]["error"] == 3
    assert summary["score"] == 55


def test_clean_dataset_gets_perfect_score() -> None:
    rows = [
        {"customer_id": "C1", "email": "a@example.com", "age": "30", "plan": "pro"},
        {"customer_id": "C2", "email": "b@example.com", "age": "25", "plan": "basic"},
    ]
    report = evaluate_rules(rows, dataset_name="customers", source="clean.csv")
    summary = build_reliability_summary(report)

    assert summary["status"] == "passed"
    assert summary["score"] == 100
    assert summary["finding_count"] == 0
