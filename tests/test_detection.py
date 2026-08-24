"""Tests for the detection agent with a fake Bedrock adapter."""

from src.agents.detection import DetectionAgent
from src.agents.contracts import DetectionInput, Priority


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def invoke_json(self, **kwargs):
        return self.payload


def test_detection_agent_returns_structured_incident() -> None:
    report = {
        "findings": [
            {"check": "uniqueness", "severity": "critical", "column": "customer_id"},
            {"check": "validity", "severity": "error", "column": "email"},
        ]
    }
    agent = DetectionAgent(FakeClient({
        "priority": "critical",
        "failed_checks": ["uniqueness"],
        "severity": "critical",
        "affected_columns": ["customer_id"],
        "evidence": [{"duplicate_count": 2}],
    }))
    incident = agent.run(DetectionInput(report, "customers"))
    assert incident.priority == Priority.CRITICAL
    assert incident.failed_checks == ("uniqueness",)
    assert incident.incident_id.startswith("INC-")


def test_detection_rejects_unknown_check() -> None:
    report = {"findings": [{"check": "validity"}]}
    agent = DetectionAgent(FakeClient({
        "priority": "high",
        "failed_checks": ["made_up"],
        "severity": "error",
        "affected_columns": [],
        "evidence": [],
    }))
    try:
        agent.run(DetectionInput(report, "customers"))
    except ValueError as exc:
        assert "unknown failed check" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
