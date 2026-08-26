from pathlib import Path

import pandas as pd


EVALUATION_DIR = Path(__file__).parents[1] / "data" / "evaluation"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(EVALUATION_DIR / name)


def test_clean_dataset_has_expected_schema_and_no_nulls():
    df = load("clean.csv")
    assert list(df.columns) == [
        "customer_id", "full_name", "email", "signup_date",
        "country", "age", "plan", "monthly_spend"
    ]
    assert df["age"].notna().all()
    assert df["email"].str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$").all()
    assert df["age"].between(0, 120).all()
    assert df["plan"].isin({"basic", "pro", "enterprise"}).all()


def test_missing_values_fixture_contains_completeness_defect():
    df = load("missing_values.csv")
    assert int(df["age"].isna().sum()) == 1


def test_invalid_values_fixture_contains_validity_defects():
    df = load("invalid_values.csv")
    assert not df["email"].str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$").all()
    assert (df["age"] < 0).any()
    assert (~df["plan"].isin({"basic", "pro", "enterprise"})).any()


def test_schema_drift_fixture_contains_unexpected_column():
    df = load("schema_drift.csv")
    expected = {
        "customer_id", "full_name", "email", "signup_date",
        "country", "age", "plan", "monthly_spend"
    }
    assert "loyalty_tier" in set(df.columns) - expected


def test_mixed_issues_fixture_contains_multiple_defect_classes():
    df = load("mixed_issues.csv")
    assert df["age"].isna().any()
    assert (~df["email"].str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")).any()
    assert (df["age"] < 0).any()
    assert (~df["plan"].isin({"basic", "pro", "enterprise"})).any()
