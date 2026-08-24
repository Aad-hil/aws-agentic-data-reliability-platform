"""Tests for the RCA agent with a fake Bedrock adapter."""

from src.agents.contracts import Incident, Priority, RCAInput
from src.agents.rca import RCAAgent


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def invoke_json(self, **kwargs):
        return self.payload


def incident():
    return Incident(
        incident_id="INC-001",
        priority=Priority.CRITICAL,
        failed_checks=("uniqueness",),
        severity="critical",
        affected_columns=("customer_id",),
        evidence=({"duplicate_count": 2},),
    )


def test_rca_returns_ranked_evidence_backed_hypotheses() -> None:
    agent = RCAAgent(FakeClient({
        "hypotheses": [
            {
                "hypothesis": "Duplicate source records",
                "evidence": ["duplicate_count=2"],
                "confidence": 0.9,
                "uncertainty": "Source lineage not confirmed",
            }
        ]
    }))
    result = agent.run(RCAInput(incident(), {"customer_id": {"unique_count": 2}}, {"row_count": 4}))
    assert result.incident_id == "INC-001"
    assert result.hypotheses[0].confidence == 0.9


def test_rca_rejects_invalid_confidence() -> None:
    agent = RCAAgent(FakeClient({
        "hypotheses": [{
            "hypothesis": "Unknown",
            "evidence": ["observed failure"],
            "confidence": 1.5,
            "uncertainty": "Unknown",
        }]
    }))
    try:
        agent.run(RCAInput(incident(), {}, {}))
    except ValueError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_rca_requires_evidence() -> None:
    agent = RCAAgent(FakeClient({
        "hypotheses": [{
            "hypothesis": "Unknown",
            "evidence": [],
            "confidence": 0.2,
            "uncertainty": "Unknown",
        }]
    }))
    try:
        agent.run(RCAInput(incident(), {}, {}))
    except ValueError as exc:
        assert "must contain evidence" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
