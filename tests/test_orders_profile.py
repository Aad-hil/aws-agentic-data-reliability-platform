"""Tests for the opt-in production orders reliability profile."""

from src.lambda_handler import _rules_for_dataset
from src.reliability.evaluator import evaluate_rules
from src.reliability.models import CheckType, Severity
from src.reliability.rules import ORDERS_QUALITY_RULES, QUALITY_RULES


CLEAN_ORDER = {
    "order_id": "O1001",
    "customer_id": "C1001",
    "order_date": "2026-08-20",
    "country": "IN",
    "plan": "pro",
    "product_category": "electronics",
    "quantity": "2",
    "unit_price": "499.99",
    "discount_rate": "0.10",
    "order_amount": "899.98",
    "payment_method": "card",
    "channel": "web",
    "status": "paid",
}


def test_orders_profile_detects_expected_domain_violations() -> None:
    row = CLEAN_ORDER.copy()
    row.update({
        "order_date": "not-a-date",
        "quantity": "0",
        "discount_rate": "1.5",
        "order_amount": "-10",
        "payment_method": "crypto",
    })

    report = evaluate_rules(
        [row],
        dataset_name="production_orders_1000_faulty",
        source="test.csv",
        rules=ORDERS_QUALITY_RULES,
    )

    assert report.finding_count == 5
    assert {finding.column for finding in report.findings} == {
        "order_date", "quantity", "discount_rate", "order_amount", "payment_method"
    }
    assert all(finding.check == CheckType.VALIDITY for finding in report.findings)
    assert all(finding.severity == Severity.ERROR for finding in report.findings)


def test_orders_profile_detects_missing_values_and_duplicate_keys() -> None:
    first = CLEAN_ORDER.copy()
    second = CLEAN_ORDER.copy()
    second["country"] = ""

    report = evaluate_rules(
        [first, second],
        dataset_name="production_orders_1000_faulty",
        source="test.csv",
        rules=ORDERS_QUALITY_RULES,
    )

    assert report.finding_count == 2
    assert {finding.check for finding in report.findings} == {
        CheckType.COMPLETENESS, CheckType.UNIQUENESS
    }


def test_orders_profile_requires_exact_expected_schema() -> None:
    row = CLEAN_ORDER.copy()
    row.pop("status")

    report = evaluate_rules(
        [row],
        dataset_name="production_orders_1000_faulty",
        source="test.csv",
        rules=ORDERS_QUALITY_RULES,
    )

    schema_findings = [f for f in report.findings if f.check == CheckType.SCHEMA]
    assert len(schema_findings) == 1
    assert schema_findings[0].severity == Severity.CRITICAL


def test_existing_customer_profile_remains_default() -> None:
    assert _rules_for_dataset("customers") is QUALITY_RULES
    assert _rules_for_dataset("mixed_issues") is QUALITY_RULES


def test_orders_profile_is_opt_in_by_dataset_prefix() -> None:
    assert _rules_for_dataset("production_orders_1000") is ORDERS_QUALITY_RULES
    assert _rules_for_dataset("production_orders_1000_faulty") is ORDERS_QUALITY_RULES
