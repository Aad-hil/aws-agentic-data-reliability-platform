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
Return JSON with exactly these fields: action, rationale, risk, evidence.
Recommendations must be advisory and must not instruct automatic destructive
data mutation. Prefer reversible, reviewable actions."""

    REPAIR_PROMPT = """Your previous response did not satisfy the required recommendation schema.
Return ONLY a JSON object containing all four fields: action, rationale, risk, evidence.
Do not add alternative field names, markdown, commentary, or prose outside the JSON object.
Use ONLY the supplied incident and RCA evidence. Recommendations must remain advisory and reviewable."""

    def __init__(self, client: BedrockClient) -> None:
        self.client = client

    def run(self, request: RecommendationInput) -> Recommendation:
        user_prompt = json.dumps(
            {
                "incident": request.incident,
                "rca": request.rca,
            },
            default=str,
        )
        payload = self.client.invoke_json(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        missing = RecommendationAgent._missing_fields(payload)
        if missing:
            payload = self.client.invoke_json(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_prompt + "\n\n" + self.REPAIR_PROMPT,
            )

        return self._parse(payload, request)

    @staticmethod
    def _missing_fields(payload: dict[str, Any]) -> list[str]:
        required = ("action", "rationale", "risk", "evidence")
        return [key for key in required if key not in payload]

    @staticmethod
    def _parse(payload: dict[str, Any], request: RecommendationInput) -> Recommendation:
        missing = RecommendationAgent._missing_fields(payload)
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
