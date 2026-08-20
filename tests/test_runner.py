"""Tests for the end-to-end local reliability runner."""

from pathlib import Path

from src.reliability.models import CheckType
from src.reliability.runner import run_reliability_checks


DATASET = Path(__file__).parents[1] / "data" / "sample" / "customers.csv"


def test_runner_returns_dataset_metadata() -> None:
    report = run_reliability_checks(DATASET)

    assert report.dataset.name == "customer_dataset"
    assert report.dataset.row_count == 50
    assert "customer_id" in report.dataset.columns


def test_runner_detects_expected_sample_failures() -> None:
    report = run_reliability_checks(DATASET)
    checks = {finding.check for finding in report.findings}

    assert CheckType.COMPLETENESS in checks
    assert CheckType.UNIQUENESS in checks
    assert CheckType.VALIDITY in checks
    assert CheckType.SCHEMA not in checks


def test_runner_produces_normalized_findings() -> None:
    report = run_reliability_checks(DATASET)

    assert report.finding_count == len(report.findings)
    assert all(finding.description for finding in report.findings)
    assert all(finding.evidence for finding in report.findings)
