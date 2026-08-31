"""Tests for Lambda production boundaries without AWS or Bedrock."""
import json
from src import lambda_handler

class Body:
    def read(self): return b"customer_id,email,status\n1001,a@example.com,active\n1001,b@example.com,active\n"
class FakeS3:
    def __init__(self): self.objects = []
    def get_object(self, **kwargs): return {"Body": Body()}
    def put_object(self, **kwargs): self.objects.append(kwargs)
class FakeCloudWatch:
    def __init__(self): self.calls = []
    def put_metric_data(self, **kwargs): self.calls.append(kwargs)
class FakeOrchestrator:
    def run(self, **kwargs):
        from src.agents.contracts import Incident, Priority, RCAResult, Recommendation, RootCauseHypothesis
        return type("Result", (), {
            "incident": Incident("INC-001", Priority.CRITICAL, ("uniqueness",), "critical", ("customer_id",), ({"duplicate_count": 1},)),
            "rca": RCAResult("INC-001", (RootCauseHypothesis("Duplicate source records", ("duplicate_count=1",), 0.9, "Lineage unconfirmed"),)),
            "recommendation": Recommendation("INC-001", "Quarantine for review", "Limit propagation", "Manual review required", ("duplicate_count=1",)),
        })()

def test_handler_processes_csv_and_publishes_duration_metric(monkeypatch):
    fake = FakeS3()
    fake_cloudwatch = FakeCloudWatch()
    monkeypatch.setattr(lambda_handler, "s3", fake)
    monkeypatch.setattr(lambda_handler, "cloudwatch", fake_cloudwatch)
    monkeypatch.setattr(lambda_handler, "build_orchestrator", lambda: FakeOrchestrator())
    result = lambda_handler.handler({"Records": [{"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "input/customers.csv"}}}]}, None)
    assert result["processed"][0]["report_key"] == "reports/customers.json"
    assert result["failures"] == []
    payload = json.loads(fake.objects[0]["Body"])
    assert payload["incident"]["incident_id"] == "INC-001"
    assert payload["recommendation"]["automatic_mutation_allowed"] is False
    assert len(fake_cloudwatch.calls) == 1
    metric = fake_cloudwatch.calls[0]
    assert metric["Namespace"] == "AgenticDataReliability"
    assert metric["MetricData"][0]["MetricName"] == "ProcessingDurationMs"
    assert metric["MetricData"][0]["Unit"] == "Milliseconds"
    assert metric["MetricData"][0]["Value"] >= 0

def test_handler_ignores_non_csv_and_report_keys(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(lambda_handler, "s3", fake)
    monkeypatch.setattr(lambda_handler, "build_orchestrator", lambda: FakeOrchestrator())
    result = lambda_handler.handler({"Records": [
        {"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "input/readme.txt"}}},
        {"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "reports/customers.json"}}},
    ]}, None)
    assert result["processed"] == []
    assert result["failures"] == []

def test_handler_isolates_record_failure(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(lambda_handler, "s3", fake)
    monkeypatch.setattr(lambda_handler, "build_orchestrator", lambda: FakeOrchestrator())
    fake.get_object = lambda **kwargs: (_ for _ in ()).throw(RuntimeError("s3 unavailable"))
    result = lambda_handler.handler({"Records": [{"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "input/customers.csv"}}}]}, None)
    assert result["processed"] == []
    assert result["failures"][0]["error"] == "RuntimeError"
