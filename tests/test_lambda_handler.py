"""Tests for Lambda orchestration without AWS or Bedrock."""
import json
from src import lambda_handler

class Body:
    def read(self):
        return b"customer_id,email,status\n1001,a@example.com,active\n1001,b@example.com,active\n"

class FakeS3:
    def __init__(self): self.objects = []
    def get_object(self, **kwargs): return {"Body": Body()}
    def put_object(self, **kwargs): self.objects.append(kwargs)

class FakeOrchestrator:
    def run(self, **kwargs):
        from src.agents.contracts import Incident, Priority, RCAResult, Recommendation, RootCauseHypothesis
        return type("Result", (), {
            "incident": Incident("INC-001", Priority.CRITICAL, ("uniqueness",), "critical", ("customer_id",), ({"duplicate_count": 1},)),
            "rca": RCAResult("INC-001", (RootCauseHypothesis("Duplicate source records", ("duplicate_count=1",), 0.9, "Lineage unconfirmed"),)),
            "recommendation": Recommendation("INC-001", "Quarantine for review", "Limit propagation", "Manual review required", ("duplicate_count=1",)),
        })()

def test_handler_runs_full_workflow(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(lambda_handler, "s3", fake)
    monkeypatch.setattr(lambda_handler, "build_orchestrator", lambda: FakeOrchestrator())
    result = lambda_handler.handler({"Records": [{"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "input/customers.csv"}}}]}, None)
    assert result["processed"][0]["report_key"] == "reports/customers.json"
    payload = json.loads(fake.objects[0]["Body"])
    assert payload["incident"]["incident_id"] == "INC-001"
    assert payload["recommendation"]["automatic_mutation_allowed"] is False

def test_handler_ignores_non_csv_and_report_keys(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(lambda_handler, "s3", fake)
    monkeypatch.setattr(lambda_handler, "build_orchestrator", lambda: FakeOrchestrator())
    result = lambda_handler.handler({"Records": [
        {"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "input/readme.txt"}}},
        {"s3": {"bucket": {"name": "demo-bucket"}, "object": {"key": "reports/customers.json"}}},
    ]}, None)
    assert result["processed"] == []
