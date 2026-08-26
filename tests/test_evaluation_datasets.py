import csv
from pathlib import Path


EVALUATION_DIR = Path(__file__).parents[1] / "data" / "evaluation"
EXPECTED_COLUMNS = [
    "customer_id", "full_name", "email", "signup_date",
    "country", "age", "plan", "monthly_spend"
]
ALLOWED_PLANS = {"basic", "pro", "enterprise"}


def load(name: str) -> list[dict[str, str]]:
    with (EVALUATION_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def valid_email(value: str) -> bool:
    return "@" in value and " " not in value and "." in value.split("@", 1)[1]


def test_clean_dataset_has_expected_schema_and_no_defects():
    rows = load("clean.csv")
    assert rows
    assert list(rows[0]) == EXPECTED_COLUMNS
    assert all(row["age"] != "" for row in rows)
    assert all(valid_email(row["email"]) for row in rows)
    assert all(0 <= int(row["age"]) <= 120 for row in rows)
    assert all(row["plan"] in ALLOWED_PLANS for row in rows)


def test_missing_values_fixture_contains_completeness_defect():
    rows = load("missing_values.csv")
    assert sum(row["age"] == "" for row in rows) == 1


def test_invalid_values_fixture_contains_validity_defects():
    rows = load("invalid_values.csv")
    assert any(not valid_email(row["email"]) for row in rows)
    assert any(int(row["age"]) < 0 for row in rows)
    assert any(row["plan"] not in ALLOWED_PLANS for row in rows)


def test_schema_drift_fixture_contains_unexpected_column():
    rows = load("schema_drift.csv")
    assert rows
    assert "loyalty_tier" in set(rows[0]) - set(EXPECTED_COLUMNS)


def test_mixed_issues_fixture_contains_multiple_defect_classes():
    rows = load("mixed_issues.csv")
    assert any(row["age"] == "" for row in rows)
    assert any(not valid_email(row["email"]) for row in rows)
    assert any(row["age"] and int(row["age"]) < 0 for row in rows)
    assert any(row["plan"] not in ALLOWED_PLANS for row in rows)
