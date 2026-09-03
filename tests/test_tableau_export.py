"""Tests for the Tableau analytical export."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build_tableau_dataset import export_reports, transform_report

FIXTURE = Path(__file__).parent / "fixtures" / "tableau_report.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_transform_report_preserves_run_and_reliability_metrics() -> None:
    dataset_run, findings, insights = transform_report(_load_fixture())
    assert dataset_run["run_id"] == "run-001"
    assert dataset_run["dataset"] == "production_orders_demo"
    assert dataset_run["row_count"] == 1005
    assert dataset_run["quality_score"] == 0
    assert dataset_run["critical_count"] == 1
    assert dataset_run["error_count"] == 6
    assert len(findings) == 7
    assert len(insights) == 2


def test_transform_report_extracts_affected_rows() -> None:
    _, findings, _ = transform_report(_load_fixture())
    country = next(item for item in findings if item["column"] == "country")
    assert country["affected_row_count"] == 2
    assert country["affected_rows"] == "81,89"


def test_transform_report_normalizes_character_by_character_agent_evidence() -> None:
    _, _, insights = transform_report(_load_fixture())
    assert insights[0]["hypothesis"] == "Duplicate order IDs"
    assert "1000 unique order IDs" in insights[0]["hypothesis_evidence"]
    assert insights[0]["recommendation_evidence"] == "The order_id column contains duplicates."
    assert len(insights[0]["recommendation_evidence"]) < 100


def test_export_reports_writes_three_tableau_csvs(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "tableau"
    reports_dir.mkdir()
    (reports_dir / "run-001.json").write_text(json.dumps(_load_fixture()), encoding="utf-8")

    counts = export_reports(reports_dir, output_dir)
    assert counts == {"reports": 1, "dataset_runs": 1, "findings": 7, "agent_insights": 2}
    assert (output_dir / "dataset_runs.csv").exists()
    assert (output_dir / "findings.csv").exists()
    assert (output_dir / "agent_insights.csv").exists()


def test_export_reports_rejects_empty_directory(tmp_path: Path) -> None:
    try:
        export_reports(tmp_path / "empty", tmp_path / "tableau")
    except FileNotFoundError as exc:
        assert "No JSON reports found" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
