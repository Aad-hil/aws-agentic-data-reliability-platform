"""Typed contracts exchanged between reliability agents."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class Priority(str, Enum):
    """Incident priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DetectionInput:
    """Evidence supplied to the detection agent."""

    reliability_report: Mapping[str, Any]
    dataset_name: str


@dataclass(frozen=True)
class Incident:
    """Structured incident selected from reliability evidence."""

    incident_id: str
    priority: Priority
    failed_checks: tuple[str, ...]
    severity: str
    affected_columns: tuple[str, ...]
    evidence: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class RCAInput:
    """Evidence supplied to the root-cause analysis agent."""

    incident: Incident
    profile: Mapping[str, Any]
    dataset_metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RootCauseHypothesis:
    """A ranked, evidence-backed root-cause hypothesis."""

    hypothesis: str
    evidence: tuple[str, ...]
    confidence: float
    uncertainty: str


@dataclass(frozen=True)
class RCAResult:
    """Structured RCA result."""

    incident_id: str
    hypotheses: tuple[RootCauseHypothesis, ...]


@dataclass(frozen=True)
class RecommendationInput:
    """Evidence supplied to the recommendation agent."""

    incident: Incident
    rca: RCAResult


@dataclass(frozen=True)
class Recommendation:
    """Advisory remediation recommendation."""

    incident_id: str
    action: str
    rationale: str
    risk: str
    evidence: tuple[str, ...]
    automatic_mutation_allowed: bool = False


@dataclass(frozen=True)
class AgentError:
    """Explicit failure state for an agent handoff."""

    agent: str
    code: str
    message: str
    recoverable: bool


def to_dict(value: Any) -> dict[str, Any]:
    """Convert a contract dataclass into JSON-friendly primitive data."""
    if not hasattr(value, "__dataclass_fields__"):
        raise TypeError("value must be a dataclass contract")
    return asdict(value)
