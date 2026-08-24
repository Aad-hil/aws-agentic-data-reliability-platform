"""End-to-end local reliability-to-agents pipeline."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.agents.orchestrator import ReliabilityOrchestrator
from src.reliability.evaluator import evaluate_rules
from src.reliability.profiler import profile_rows
from src.reliability.report import build_reliability_summary


def load_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load a CSV into simple row mappings for the reliability engine."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def run_local_pipeline(
    dataset_path: str | Path,
    *,
    orchestrator: ReliabilityOrchestrator,
) -> dict[str, Any]:
    """Run deterministic checks followed by the multi-agent workflow."""
    path = Path(dataset_path)
    rows = load_csv(path)
    dataset_name = path.stem

    profile = profile_rows(
        rows,
        dataset_name=dataset_name,
        source=str(path),
    )
    report = evaluate_rules(
        rows,
        dataset_name=dataset_name,
        source=str(path),
    )
    summary = build_reliability_summary(report)

    workflow = orchestrator.run(
        reliability_report=summary,
        dataset_name=dataset_name,
        profile=profile,
        dataset_metadata=summary["dataset"],
    )

    return {
        "reliability_report": summary,
        "incident": workflow.incident,
        "rca": workflow.rca,
        "recommendation": workflow.recommendation,
    }


def result_to_json(result: dict[str, Any]) -> str:
    """Serialize a pipeline result for logs or API responses."""
    from dataclasses import asdict

    payload = {
        key: asdict(value) if hasattr(value, "__dataclass_fields__") else value
        for key, value in result.items()
    }
    return json.dumps(payload, indent=2, default=str)
