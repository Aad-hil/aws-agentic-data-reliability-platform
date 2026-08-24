"""Tests for the S3-to-Lambda execution boundary."""

import json

from src import lambda_handler


class Body:
    def read(self):
        return b"customer_id,email,status\n1001,a@example.com,active\n1001,b@example.com,active\n"


class FakeS3:
    def __init__(self):
        self.objects = []

    def get_object(self, **kwargs):
        return {"Body": Body()}

    def put_object(self, **kwargs):
        self.objects.append(kwargs)


def test_handler_reads_input_and_writes_report(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(lambda_handler, "s3", fake)

    result = lambda_handler.handler({
        "Records": [{
            "s3": {
                "bucket": {"name": "demo-bucket"},
                "object": {"key": "input/customers.csv"},
            }
        }]
    }, None)

    assert result["processed"][0]["input_key"] == "input/customers.csv"
    assert result["processed"][0]["report_key"] == "reports/customers.json"
    payload = json.loads(fake.objects[0]["Body"])
    assert payload["status"] == "failed"


def test_handler_ignores_non_input_keys(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(lambda_handler, "s3", fake)

    result = lambda_handler.handler({
        "Records": [{
            "s3": {
                "bucket": {"name": "demo-bucket"},
                "object": {"key": "reports/existing.json"},
            }
        }]
    }, None)

    assert result["processed"] == []
    assert fake.objects == []
