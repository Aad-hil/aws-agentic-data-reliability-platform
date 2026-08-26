"""Contract-level evaluation of agent outputs without calling Bedrock."""

import pytest

from src.agents.contracts import DetectionInput, Incident, Priority, RCAInput, RecommendationInput
from src.agents.detection import DetectionAgent
from src.agents.rca import RCAAgent
from src.agents.recommendation import RecommendationAgent


class FakeBedrock:
    def __init__(self, payload):
        self.payload = payload

    def invoke_json(self, **_kwargs):
        return self.payload


REPORT = {
    "findings": [
        {"check": "completeness", "severity": "error", "column": "age"},
        {"check": "validity", "severity": "error", "column": "email"},
        {"check": "validity", "severity": "error", "column": "age"},
        {"check": "validity", "severity": "error", "column": "plan"},
        {"check": "schema", "severity": "warning", "column": None},
    ]
}


def test_detection_accepts_only_evidence_supported_checks():
    payload = {
        "incident_id": "customers-e2e-003",
        "priority": "high",
        "failed_checks": ["completeness", "validity"],
        "severity": "error",
        "affected_columns": ["age", "email", "plan"],
        "evidence": [{"value": "age is missing"}],
    }
    incident = DetectionAgent(FakeBedrock(payload)).run(
        DetectionInput(reliability_report=REPORT, dataset_name="customers-e2e-003")
    )
    assert incident.priority is Priority.HIGH
    assert set(incident.failed_checks) <= {"completeness", "validity", "schema"}
    assert set(incident.affected_columns) >= {"age", "email", "plan"}


def test_detection_rejects_hallucinated_check():
    payload = {
        "priority": "high",
        "failed_checks": ["completeness", "fabricated_check"],
        "severity": "error",
        "affected_columns": ["age"],
        "evidence": [{"value": "evidence"}],
    }
    with pytest.raises(ValueError, match="unknown failed check"):
        DetectionAgent(FakeBedrock(payload)).run(
            DetectionInput(reliability_report=REPORT, dataset_name="customers-e2e-003")
        )


def test_rca_requires_evidence_and_bounded_confidence():
    incident = Incident(
        incident_id="customers-e2e-003",
        priority=Priority.HIGH,
        failed_checks=("completeness", "validity"),
        severity="error",
        affected_columns=("age", "email"),
        evidence=({"value": "age missing"},),
    )
    payload = {
        "hypotheses": [
            {
                "hypothesis": "Data entry errors caused invalid values.",
                "evidence": ["age contains a missing value"],
                "confidence": 0.8,
                "uncertainty": "Moderate",
            }
        ]
    }
    result = RCAAgent(FakeBedrock(payload)).run(
        RCAInput(incident=incident, profile={}, dataset_metadata={"row_count": 50})
    )
    assert result.hypotheses[0].confidence == 0.8
    assert result.hypotheses[0].evidence


def test_rca_rejects_unbounded_confidence():
    incident = Incident("id", Priority.HIGH, ("validity",), "error", ("age",), ({"value": "-5"},))
    payload = {
        "hypotheses": [{
            "hypothesis": "Bad data",
            "evidence": ["age is negative"],
            "confidence": 1.2,
            "uncertainty": "Low",
        }]
    }
    with pytest.raises(ValueError, match="between 0 and 1"):
        RCAAgent(FakeBedrock(payload)).run(RCAInput(incident, {}, {}))


def test_recommendation_is_always_advisory():
    incident = Incident("id", Priority.HIGH, ("validity",), "error", ("age",), ({"value": "-5"},))
    payload = {
        "action": "Review and correct the invalid age value.",
        "rationale": "The value is outside the allowed range.",
        "risk": "Medium",
        "evidence": ["age must be between 0 and 120"],
    }
    recommendation = RecommendationAgent(FakeBedrock(payload)).run(
        RecommendationInput(incident=incident, rca=None)
    )
    assert recommendation.automatic_mutation_allowed is False
    assert recommendation.evidence
    assert recommendation.action
