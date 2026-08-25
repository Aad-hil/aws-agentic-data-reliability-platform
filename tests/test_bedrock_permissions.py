"""Contract tests for the Lambda Bedrock permission boundary."""

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "infra" / "template.yaml"


class CloudFormationLoader(yaml.SafeLoader):
    """Safe YAML loader that preserves CloudFormation intrinsic tags."""


def _construct_intrinsic(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


CloudFormationLoader.add_multi_constructor("!", _construct_intrinsic)


def test_lambda_can_invoke_bedrock_models():
    template = yaml.load(TEMPLATE.read_text(), Loader=CloudFormationLoader)
    policies = template["Resources"]["ReliabilityFunction"]["Properties"]["Policies"]
    statement = policies[2]["Statement"][0]
    assert "bedrock:InvokeModel" in statement["Action"]
    assert statement["Resource"] == "*"
