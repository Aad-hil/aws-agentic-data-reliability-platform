"""Detection agent: prioritize incidents from deterministic evidence."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from .bedrock import BedrockClient
from .contracts import DetectionInput, Incident, Priority


class DetectionAgent:
    """Use Bedrock to prioritize a reliability incident without inventing failures."""

    SYSTEM_PROMPT = """You are a data reliability detection agent.
Use ONLY the supplied reliability report evidence.
Do not invent failed checks, columns, counts, or causes.
Select the highest-priority incident and return JSON with:
incident_id, priority, failed_checks, severity, affected_columns, evidence.
priority must be one of low, medium, high, critical.
evidence must be copied or summarized from supplied evidence only."""

    def __init__(self, client: BedrockClient) -> None:
        self.client = client

    def run(self, request: DetectionInput) -> Incident:
        payload = self.client.invoke_json(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=json.dumps(
                {
                    "dataset_name": request.dataset_name,
                    "reliability_report": request.reliability_report,
                },
                default=str,
            ),
        )
        return self._parse(payload, request)

    def _parse(self, payload: dict[str, Any], request: DetectionInput) -> Incident:
        required = ("priority", "failed_checks", "severity", "affected_columns", "evidence")
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Detection response missing fields: {', '.join(missing)}")

        report = request.reliability_report
        findings = report.get("findings", [])
        allowed_checks = {str(f.get("check")) for f in findings}
        checks = tuple(str(value) for value in payload["failed_checks"])
        if not set(checks).issubset(allowed_checks):
            raise ValueError("Detection response referenced an unknown failed check")

        priority = Priority(str(payload["priority"]).lower())
        incident_id = str(payload.get("incident_id") or self._incident_id(request.dataset_name, checks))
        raw_evidence = payload["evidence"]
        if isinstance(raw_evidence, str):
            evidence = ({"value": raw_evidence},)
        elif isinstance(raw_evidence, dict):
            evidence = (raw_evidence,)
        elif isinstance(raw_evidence, (list, tuple)):
            evidence = tuple(
                item if isinstance(item, dict) else {"value": item}
                for item in raw_evidence
            )
        else:
            raise ValueError("Detection response evidence must be a string, object, or list")
        return Incident(
            incident_id=incident_id,
            priority=priority,
            failed_checks=checks,
            severity=str(payload["severity"]),
            affected_columns=tuple(str(value) for value in payload["affected_columns"]),
            evidence=evidence,
        )

    @staticmethod
    def _incident_id(dataset_name: str, checks: tuple[str, ...]) -> str:
        digest = sha256(f"{dataset_name}:{','.join(checks)}".encode()).hexdigest()[:10]
        return f"INC-{digest.upper()}"
