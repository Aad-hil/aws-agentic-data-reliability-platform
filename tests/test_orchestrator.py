"""Tests for sequential multi-agent orchestration."""

from src.agents.contracts import (
    Incident,
    Priority,
    RCAResult,
    Recommendation,
    RootCauseHypothesis,
)
from src.agents.orchestrator import ReliabilityOrchestrator


class FakeDetection:
    def run(self, request):
        assert request.dataset_name == "customers"
        return Incident(
            incident_id="INC-001",
            priority=Priority.HIGH,
            failed_checks=("uniqueness",),
            severity="error",
            affected_columns=("customer_id",),
            evidence=({"duplicate_count": 2},),
        )


class FakeRCA:
    def run(self, request):
        assert request.incident.incident_id == "INC-001"
        return RCAResult(
            incident_id="INC-001",
            hypotheses=(
                RootCauseHypothesis(
                    hypothesis="Duplicate source records",
                    evidence=("duplicate_count=2",),
                    confidence=0.9,
                    uncertainty="Lineage not confirmed",
                ),
            ),
        )


class FakeRecommendation:
    def run(self, request):
        assert request.incident.incident_id == request.rca.incident_id
        return Recommendation(
            incident_id=request.incident.incident_id,
            action="Quarantine for review",
            rationale="Prevents propagation.",
            risk="Requires review.",
            evidence=("duplicate_count=2",),
        )


def test_orchestrator_preserves_agent_handoff_order() -> None:
    result = ReliabilityOrchestrator(
        FakeDetection(), FakeRCA(), FakeRecommendation()
    ).run(
        reliability_report={"findings": [{"check": "uniqueness"}]},
        dataset_name="customers",
        profile={"customer_id": {"unique_count": 2}},
        dataset_metadata={"row_count": 4},
    )

    assert result.incident.incident_id == "INC-001"
    assert result.rca.incident_id == "INC-001"
    assert result.recommendation.incident_id == "INC-001"
    assert result.recommendation.automatic_mutation_allowed is False
