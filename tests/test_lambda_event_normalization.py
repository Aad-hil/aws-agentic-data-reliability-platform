"""Tests for normalizing S3 and EventBridge S3 event shapes."""

from src.lambda_handler import _normalize_records


def test_normalize_native_s3_records():
    event = {
        "Records": [
            {"s3": {"bucket": {"name": "bucket"}, "object": {"key": "input/customers.csv"}}}
        ]
    }

    records = _normalize_records(event)

    assert records[0]["s3"]["bucket"]["name"] == "bucket"
    assert records[0]["s3"]["object"]["key"] == "input/customers.csv"


def test_normalize_eventbridge_s3_object_created():
    event = {
        "source": "aws.s3",
        "detail-type": "Object Created",
        "detail": {
            "bucket": {"name": "bucket"},
            "object": {"key": "input/customers.csv"},
        },
    }

    records = _normalize_records(event)

    assert records == [
        {"s3": {"bucket": {"name": "bucket"}, "object": {"key": "input/customers.csv"}}}
    ]


def test_normalize_unknown_event_returns_no_records():
    assert _normalize_records({"source": "aws.s3"}) == []
