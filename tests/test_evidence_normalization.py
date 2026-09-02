"""Regression tests for agent evidence normalization."""

from src.agents.contracts import (
    DetectionInput,
    Incident,
    Priority,
    RCAResult,
    RecommendationInput,
    RootCauseHypothesis,
)
from src.agents.detection import DetectionAgent
from src.agents.recommendation import RecommendationAgent


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def invoke_json(self, **kwargs):
        return self.payload


def _request() -> RecommendationInput:
    incident = Incident(
        incident_id="INC-001",
        priority=Priority.CRITICAL,
        failed_checks=("uniqueness",),
        severity="critical",
        affected_columns=("order_id",),
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


def test_detection_string_evidence_is_one_value() -> None:
    report = {"findings": [{"check": "uniqueness"}]}
    agent = DetectionAgent(FakeClient({
        "priority": "critical",
        "failed_checks": ["uniqueness"],
        "severity": "critical",
        "affected_columns": ["order_id"],
        "evidence": "5 duplicate key values detected.",
    }))

    incident = agent.run(DetectionInput(report, "orders"))

    assert incident.evidence == ({"value": "5 duplicate key values detected."},)


def test_recommendation_string_evidence_is_one_value() -> None:
    agent = RecommendationAgent(FakeClient({
        "action": "Quarantine duplicate records for review",
        "rationale": "Prevents downstream propagation.",
        "risk": "Requires manual review.",
        "evidence": "5 duplicate rows require review.",
    }))

    result = agent.run(_request())

    assert result.evidence == ("5 duplicate rows require review.",)
