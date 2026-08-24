"""End-to-end local pipeline test with fake agents."""

from pathlib import Path

from src.agents.contracts import Incident, Priority, RCAResult, Recommendation, RootCauseHypothesis
from src.agents.orchestrator import ReliabilityOrchestrator
from src.pipeline import run_local_pipeline


class FakeDetection:
    def run(self, request):
        assert request.reliability_report["status"] == "failed"
        assert "uniqueness" in [f["check"] for f in request.reliability_report["findings"]]
        return Incident("INC-LOCAL-001", Priority.CRITICAL, ("uniqueness",), "critical", ("customer_id",), ({"duplicate_values": {"1001": 2}},))


class FakeRCA:
    def run(self, request):
        assert request.incident.incident_id == "INC-LOCAL-001"
        assert request.profile["row_count"] > 0
        return RCAResult("INC-LOCAL-001", (RootCauseHypothesis("Duplicate source records", ("duplicate customer_id",), 0.9, "Source lineage not confirmed"),))


class FakeRecommendation:
    def run(self, request):
        assert request.rca.incident_id == request.incident.incident_id
        return Recommendation("INC-LOCAL-001", "Quarantine duplicates for review", "Prevents downstream propagation.", "Requires manual review.", ("duplicate customer_id",))


def test_local_pipeline_connects_reliability_core_to_agents():
    dataset = Path("data/sample/customers.csv")
    result = run_local_pipeline(
        dataset,
        orchestrator=ReliabilityOrchestrator(FakeDetection(), FakeRCA(), FakeRecommendation()),
    )
    assert result["reliability_report"]["status"] == "failed"
    assert result["incident"].incident_id == "INC-LOCAL-001"
    assert result["rca"].incident_id == "INC-LOCAL-001"
    assert result["recommendation"].automatic_mutation_allowed is False
