"""Static deployment-contract tests that do not require AWS credentials."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "infra" / "template.yaml"
PARAMETERS = ROOT / "infra" / "parameters.example.json"


class CloudFormationLoader(yaml.SafeLoader):
    """Safe YAML loader that preserves CloudFormation intrinsic tags."""


def _construct_intrinsic(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


CloudFormationLoader.add_multi_constructor("!", _construct_intrinsic)


def load_template():
    return yaml.load(TEMPLATE.read_text(), Loader=CloudFormationLoader)


def test_sam_template_has_expected_runtime_and_resources():
    template = load_template()
    assert template["AWSTemplateFormatVersion"] == "2010-09-09"
    assert template["Transform"] == "AWS::Serverless-2016-10-31"
    resources = template["Resources"]
    assert "ReliabilityBucket" in resources
    assert "ReliabilityFunction" in resources
    assert "ReliabilityLogGroup" in resources
    assert "Dashboard" in resources


def test_lambda_is_triggered_only_from_input_prefix():
    template = load_template()
    event = template["Resources"]["ReliabilityFunction"]["Properties"]["Events"]["InputUpload"]
    rules = event["Properties"]["Filter"]["S3Key"]["Rules"]
    assert {"Name": "prefix", "Value": "input/"} in rules


def test_example_parameters_contain_no_real_account_values():
    params = json.loads(PARAMETERS.read_text())
    model = params["Parameters"]["BedrockModelId"]
    assert "REPLACE_WITH" in model
