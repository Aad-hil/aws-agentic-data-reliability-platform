"""Sequential orchestration for the reliability agent workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .contracts import (
    DetectionInput,
    Incident,
    RCAInput,
    RCAResult,
    Recommendation,
    RecommendationInput,
)
from .detection import DetectionAgent
from .rca import RCAAgent
from .recommendation import RecommendationAgent


@dataclass(frozen=True)
class WorkflowResult:
    """Validated outputs produced by the sequential agent workflow."""

    incident: Incident
    rca: RCAResult
    recommendation: Recommendation


class ReliabilityOrchestrator:
    """Run Detection -> RCA -> Recommendation with typed handoffs."""

    def __init__(
        self,
        detection_agent: DetectionAgent,
        rca_agent: RCAAgent,
        recommendation_agent: RecommendationAgent,
    ) -> None:
        self.detection_agent = detection_agent
        self.rca_agent = rca_agent
        self.recommendation_agent = recommendation_agent

    def run(
        self,
        *,
        reliability_report: Mapping[str, Any],
        dataset_name: str,
        profile: Mapping[str, Any],
        dataset_metadata: Mapping[str, Any],
    ) -> WorkflowResult:
        incident = self.detection_agent.run(
            DetectionInput(
                reliability_report=reliability_report,
                dataset_name=dataset_name,
            )
        )
        rca = self.rca_agent.run(
            RCAInput(
                incident=incident,
                profile=profile,
                dataset_metadata=dataset_metadata,
            )
        )
        recommendation = self.recommendation_agent.run(
            RecommendationInput(
                incident=incident,
                rca=rca,
            )
        )
        return WorkflowResult(
            incident=incident,
            rca=rca,
            recommendation=recommendation,
        )
