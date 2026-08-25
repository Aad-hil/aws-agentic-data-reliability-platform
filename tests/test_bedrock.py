"""Tests for the Bedrock adapter retry and parsing boundaries."""
import pytest
from src.agents.bedrock import BedrockClient

class ThrottledThenSuccess:
    def __init__(self): self.calls = 0
    def converse(self, **kwargs):
        self.calls += 1
        if self.calls < 3:
            raise type("ThrottlingException", (Exception,), {})("throttle")
        return {"output": {"message": {"content": [{"text": "{\"ok\": true}"}]}}}

def test_bedrock_retries_transient_errors(monkeypatch):
    client = BedrockClient(model_id="test", client=ThrottledThenSuccess(), base_delay_seconds=0)
    monkeypatch.setattr("src.agents.bedrock.random.uniform", lambda *_: 0)
    monkeypatch.setattr("src.agents.bedrock.time.sleep", lambda *_: None)
    assert client.invoke_json(system_prompt="system", user_prompt="user") == {"ok": True}

def test_bedrock_rejects_invalid_json():
    class Fake:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "not-json"}]}}}
    client = BedrockClient(model_id="test", client=Fake(), max_attempts=1)
    with pytest.raises(ValueError, match="invalid JSON"):
        client.invoke_json(system_prompt="system", user_prompt="user")

def test_bedrock_accepts_fenced_json():
    class Fake:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "```json\n{\"ok\": true}\n```"}]}}}
    client = BedrockClient(model_id="test", client=Fake(), max_attempts=1)
    assert client.invoke_json(system_prompt="system", user_prompt="user") == {"ok": True}

def test_bedrock_extracts_json_with_surrounding_text():
    class Fake:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "Here is the result: {\"ok\": true}"}]}}}
    client = BedrockClient(model_id="test", client=Fake(), max_attempts=1)
    assert client.invoke_json(system_prompt="system", user_prompt="user") == {"ok": True}

def test_bedrock_rejects_non_object_json():
    class Fake:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "[1, 2, 3]"}]}}}
    client = BedrockClient(model_id="test", client=Fake(), max_attempts=1)
    with pytest.raises(ValueError, match="must be a JSON object"):
        client.invoke_json(system_prompt="system", user_prompt="user")
