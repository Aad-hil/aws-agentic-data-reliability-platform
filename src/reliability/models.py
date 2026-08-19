"""Normalized models used by the data reliability engine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Impact level assigned to a reliability finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CheckType(str, Enum):
    """Reliability check categories."""

    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"
    SCHEMA = "schema"


@dataclass(frozen=True)
class ReliabilityFinding:
    """A normalized, explainable data reliability finding."""

    check: CheckType
    severity: Severity
    description: str
    column: str | None = None
    observed_value: Any = None
    expected_value: Any = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DatasetMetadata:
    """Metadata describing the dataset under inspection."""

    name: str
    source: str
    row_count: int
    columns: tuple[str, ...]


@dataclass(frozen=True)
class ReliabilityReport:
    """Result returned by the reliability engine."""

    dataset: DatasetMetadata
    findings: tuple[ReliabilityFinding, ...]

    @property
    def finding_count(self) -> int:
        """Return the number of findings in the report."""

        return len(self.findings)
