"""Root-cause analysis agent for reliability incidents."""

from __future__ import annotations

import json
from typing import Any

from .bedrock import BedrockClient
from .contracts import RCAInput, RCAResult, RootCauseHypothesis


class RCAAgent:
    """Generate evidence-backed root-cause hypotheses."""

    SYSTEM_PROMPT = """You are a data reliability root-cause analysis agent.
Use ONLY the supplied incident, profile, and dataset metadata.
Do not claim a root cause is proven unless the evidence proves it.
Return JSON with a 'hypotheses' array. Each item must contain:
hypothesis, evidence (array of strings), confidence (0 to 1), uncertainty.
Rank hypotheses from most to least plausible."""

    def __init__(self, client: BedrockClient) -> None:
        self.client = client

    def run(self, request: RCAInput) -> RCAResult:
        payload = self.client.invoke_json(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=json.dumps(
                {
                    "incident": {
                        "incident_id": request.incident.incident_id,
                        "priority": request.incident.priority.value,
                        "failed_checks": request.incident.failed_checks,
                        "severity": request.incident.severity,
                        "affected_columns": request.incident.affected_columns,
                        "evidence": request.incident.evidence,
                    },
                    "profile": request.profile,
                    "dataset_metadata": request.dataset_metadata,
                },
                default=str,
            ),
        )
        return self._parse(payload, request)

    @staticmethod
    def _parse(payload: dict[str, Any], request: RCAInput) -> RCAResult:
        hypotheses = payload.get("hypotheses")
        if not isinstance(hypotheses, list) or not hypotheses:
            raise ValueError("RCA response must contain a non-empty hypotheses array")

        results = []
        for item in hypotheses:
            if not isinstance(item, dict):
                raise ValueError("Each RCA hypothesis must be an object")
            required = ("hypothesis", "evidence", "confidence", "uncertainty")
            missing = [key for key in required if key not in item]
            if missing:
                raise ValueError(f"RCA hypothesis missing fields: {', '.join(missing)}")
            confidence = float(item["confidence"])
            if not 0 <= confidence <= 1:
                raise ValueError("RCA confidence must be between 0 and 1")
            evidence = tuple(str(value) for value in item["evidence"])
            if not evidence:
                raise ValueError("RCA hypotheses must contain evidence")
            results.append(
                RootCauseHypothesis(
                    hypothesis=str(item["hypothesis"]),
                    evidence=evidence,
                    confidence=confidence,
                    uncertainty=str(item["uncertainty"]),
                )
            )

        return RCAResult(
            incident_id=request.incident.incident_id,
            hypotheses=tuple(results),
        )
