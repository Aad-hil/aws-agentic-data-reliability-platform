"""Tests for the dataset profiler."""

from src.reliability.profiler import profile_rows

ROWS = [
    {"customer_id": "C1", "age": "30", "spend": "49.50"},
    {"customer_id": "C2", "age": "", "spend": "19.00"},
    {"customer_id": "C3", "age": "42", "spend": "199.00"},
    {"customer_id": "C3", "age": "42", "spend": "199.00"},
]


def test_profile_reports_dataset_shape_and_duplicates() -> None:
    profile = profile_rows(ROWS, dataset_name="customers", source="test.csv")
    assert profile["row_count"] == 4
    assert profile["column_count"] == 3
    assert profile["duplicate_row_count"] == 1


def test_profile_reports_column_metrics() -> None:
    profile = profile_rows(ROWS, dataset_name="customers", source="test.csv")
    assert profile["columns"]["age"]["dtype"] == "integer"
    assert profile["columns"]["age"]["null_count"] == 1
    assert profile["columns"]["age"]["null_percentage"] == 25.0
    assert profile["columns"]["age"]["min"] == 30
    assert profile["columns"]["age"]["max"] == 42


def test_profile_reports_freshness_dates() -> None:
    rows = [{"signup_date": "2026-08-01"}, {"signup_date": "2026-08-18"}, {"signup_date": "bad-date"}]
    profile = profile_rows(rows, dataset_name="customers", source="test.csv", freshness_column="signup_date")
    assert profile["freshness"]["min_date"] == "2026-08-01"
    assert profile["freshness"]["max_date"] == "2026-08-18"
    assert profile["freshness"]["invalid_date_count"] == 1
