"""Remediation recommendation agent."""

from __future__ import annotations

import json
from typing import Any

from .bedrock import BedrockClient
from .contracts import Recommendation, RecommendationInput


class RecommendationAgent:
    """Turn RCA evidence into a safe, advisory remediation recommendation."""

    SYSTEM_PROMPT = """You are a data reliability remediation advisor.
Use ONLY the supplied incident and RCA evidence.
Return JSON with: action, rationale, risk, evidence.
Recommendations must be advisory and must not instruct automatic destructive
data mutation. Prefer reversible, reviewable actions."""

    def __init__(self, client: BedrockClient) -> None:
        self.client = client

    def run(self, request: RecommendationInput) -> Recommendation:
        payload = self.client.invoke_json(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=json.dumps(
                {
                    "incident": request.incident,
                    "rca": request.rca,
                },
                default=str,
            ),
        )
        return self._parse(payload, request)

    @staticmethod
    def _parse(payload: dict[str, Any], request: RecommendationInput) -> Recommendation:
        required = ("action", "rationale", "risk", "evidence")
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(
                f"Recommendation response missing fields: {', '.join(missing)}"
            )

        evidence = tuple(str(value) for value in payload["evidence"])
        if not evidence:
            raise ValueError("Recommendation must contain evidence")

        return Recommendation(
            incident_id=request.incident.incident_id,
            action=str(payload["action"]),
            rationale=str(payload["rationale"]),
            risk=str(payload["risk"]),
            evidence=evidence,
            automatic_mutation_allowed=False,
        )
