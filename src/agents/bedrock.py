"""Small Bedrock Runtime adapter used by the agent layer."""

from __future__ import annotations

import json
from typing import Any, Callable


class BedrockClient:
    """Invoke an Amazon Bedrock model without embedding AWS logic in agents."""

    def __init__(
        self,
        *,
        model_id: str,
        region_name: str = "us-east-1",
        client: Any | None = None,
    ) -> None:
        self.model_id = model_id
        if client is not None:
            self._client = client
        else:
            import boto3
            self._client = boto3.client("bedrock-runtime", region_name=region_name)

    def invoke(self, *, system_prompt: str, user_prompt: str) -> str:
        """Invoke a model and return its text response.

        The request format is intentionally isolated here so individual agents
        do not depend on the Bedrock SDK response shape.
        """
        response = self._client.converse(
            modelId=self.model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
        )
        return response["output"]["message"]["content"][0]["text"]

    def invoke_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        parser: Callable[[dict[str, Any]], Any] | None = None,
    ) -> Any:
        """Invoke the model and parse a JSON object from its response."""
        raw = self.invoke(
            system_prompt=system_prompt,
            user_prompt=(
                user_prompt
                + "\n\nReturn ONLY a valid JSON object. No markdown fences."
            ),
        )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("Bedrock returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("Bedrock response must be a JSON object")
        return parser(payload) if parser else payload
