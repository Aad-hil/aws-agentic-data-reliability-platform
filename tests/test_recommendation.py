"""Tests for the recommendation agent with a fake Bedrock adapter."""

from src.agents.contracts import (
    Incident,
    Priority,
    RCAResult,
    RecommendationInput,
    RootCauseHypothesis,
)
from src.agents.recommendation import RecommendationAgent


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def invoke_json(self, **kwargs):
        return self.payload


def request():
    incident = Incident(
        incident_id="INC-001",
        priority=Priority.CRITICAL,
        failed_checks=("uniqueness",),
        severity="critical",
        affected_columns=("customer_id",),
        evidence=({"duplicate_count": 2},),
    )
    rca = RCAResult(
        incident_id="INC-001",
        hypotheses=(
            RootCauseHypothesis(
                hypothesis="Duplicate source records",
                evidence=("duplicate_count=2",),
                confidence=0.9,
                uncertainty="Source lineage not confirmed",
            ),
        ),
    )
    return RecommendationInput(incident=incident, rca=rca)


def test_recommendation_is_advisory() -> None:
    agent = RecommendationAgent(FakeClient({
        "action": "Quarantine duplicate records for review",
        "rationale": "Prevents downstream propagation.",
        "risk": "Requires manual review.",
        "evidence": ["duplicate_count=2"],
    }))
    result = agent.run(request())
    assert result.incident_id == "INC-001"
    assert result.automatic_mutation_allowed is False
    assert result.evidence == ("duplicate_count=2",)


def test_recommendation_requires_evidence() -> None:
    agent = RecommendationAgent(FakeClient({
        "action": "Delete duplicates",
        "rationale": "Cleanup",
        "risk": "Potential data loss",
        "evidence": [],
    }))
    try:
        agent.run(request())
    except ValueError as exc:
        assert "must contain evidence" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
