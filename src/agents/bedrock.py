"""Small Bedrock Runtime adapter used by the agent layer."""
from __future__ import annotations

import json
import logging
import random
import re
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class BedrockClient:
    """Invoke Bedrock with bounded retries for transient runtime failures."""

    def __init__(self, *, model_id: str, region_name: str = "us-east-1", client: Any | None = None,
                 max_attempts: int = 3, base_delay_seconds: float = 0.5) -> None:
        self.model_id = model_id
        self.max_attempts = max(1, max_attempts)
        self.base_delay_seconds = base_delay_seconds
        if client is not None:
            self._client = client
        else:
            import boto3
            self._client = boto3.client("bedrock-runtime", region_name=region_name)

    def invoke(self, *, system_prompt: str, user_prompt: str) -> str:
        request = {
            "modelId": self.model_id,
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
        }
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self._client.converse(**request)
                return response["output"]["message"]["content"][0]["text"]
            except Exception as exc:
                if attempt == self.max_attempts or not self._is_retryable(exc):
                    logger.exception("Bedrock invocation failed", extra={"attempt": attempt, "model_id": self.model_id})
                    raise
                delay = self.base_delay_seconds * (2 ** (attempt - 1)) + random.uniform(0, 0.25)
                logger.warning("Retrying Bedrock invocation", extra={"attempt": attempt, "delay_seconds": delay})
                time.sleep(delay)
        raise RuntimeError("unreachable")

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        name = exc.__class__.__name__
        return name in {"ThrottlingException", "TooManyRequestsException", "ServiceUnavailableException", "InternalServerException"}

    @staticmethod
    def _parse_json_object(raw: str) -> dict[str, Any]:
        """Parse a JSON object from a model response with common formatting noise."""
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()

        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            decoder = json.JSONDecoder()
            for index, char in enumerate(text):
                if char != "{":
                    continue
                try:
                    payload, _ = decoder.raw_decode(text[index:])
                    break
                except json.JSONDecodeError:
                    continue
            else:
                raise ValueError("Bedrock returned invalid JSON") from None

        if not isinstance(payload, dict):
            raise ValueError("Bedrock response must be a JSON object")
        return payload

    def invoke_json(self, *, system_prompt: str, user_prompt: str,
                    parser: Callable[[dict[str, Any]], Any] | None = None) -> Any:
        raw = self.invoke(system_prompt=system_prompt,
                          user_prompt=user_prompt + "\n\nReturn ONLY a valid JSON object. No markdown fences.")
        payload = self._parse_json_object(raw)
        return parser(payload) if parser else payload
