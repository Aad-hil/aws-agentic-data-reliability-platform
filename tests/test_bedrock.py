"""Tests for the Bedrock adapter using a fake client."""

from src.agents.bedrock import BedrockClient


class FakeBedrock:
    def __init__(self) -> None:
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        return {"output": {"message": {"content": [{"text": '{"ok": true}'}]}}}


def test_bedrock_client_isolates_runtime_call() -> None:
    fake = FakeBedrock()
    client = BedrockClient(model_id="test-model", client=fake)

    result = client.invoke_json(system_prompt="system", user_prompt="hello")

    assert result == {"ok": True}
    assert fake.calls[0]["modelId"] == "test-model"
    assert fake.calls[0]["messages"][0]["role"] == "user"


def test_invalid_json_is_rejected() -> None:
    class InvalidClient:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "not json"}]}}}

    client = BedrockClient(model_id="test-model", client=InvalidClient())

    try:
        client.invoke_json(system_prompt="system", user_prompt="hello")
    except ValueError as exc:
        assert "invalid JSON" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
