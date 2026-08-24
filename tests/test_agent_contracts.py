"""Tests for typed agent handoff contracts."""

from src.agents.contracts import (
    AgentError,
    Incident,
    Priority,
    RCAResult,
    Recommendation,
    RootCauseHypothesis,
    to_dict,
)


def test_contracts_are_structured_and_serializable() -> None:
    incident = Incident(
        incident_id="INC-001",
        priority=Priority.HIGH,
        failed_checks=("uniqueness",),
        severity="critical",
        affected_columns=("customer_id",),
        evidence=({"duplicate_count": 2},),
    )
    rca = RCAResult(
        incident_id=incident.incident_id,
        hypotheses=(
            RootCauseHypothesis(
                hypothesis="Duplicate source records",
                evidence=("duplicate_count=2",),
                confidence=0.9,
                uncertainty="Source lineage not yet confirmed",
            ),
        ),
    )
    recommendation = Recommendation(
        incident_id=incident.incident_id,
        action="Quarantine duplicate records for review",
        rationale="Prevents duplicate records from reaching downstream consumers.",
        risk="Manual review is required before deletion.",
        evidence=("duplicate_count=2",),
    )

    payload = to_dict(recommendation)

    assert payload["incident_id"] == "INC-001"
    assert payload["automatic_mutation_allowed"] is False
    assert to_dict(rca)["hypotheses"][0]["confidence"] == 0.9


def test_agent_error_is_explicit() -> None:
    error = AgentError(
        agent="rca",
        code="MODEL_TIMEOUT",
        message="Model request timed out.",
        recoverable=True,
    )

    assert to_dict(error)["recoverable"] is True
