"""Static deployment-contract tests that do not require AWS credentials."""

from pathlib import Path
import yaml

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "infra" / "template.yaml"
PARAMETERS = ROOT / "infra" / "parameters.example.json"


def test_sam_template_has_expected_runtime_and_resources():
    template = yaml.safe_load(TEMPLATE.read_text())
    assert template["AWSTemplateFormatVersion"] == "2010-09-09"
    assert template["Transform"] == "AWS::Serverless-2016-10-31"
    resources = template["Resources"]
    assert "ReliabilityBucket" in resources
    assert "ReliabilityFunction" in resources
    assert "ReliabilityLogGroup" in resources
    assert "Dashboard" in resources


def test_lambda_is_triggered_only_from_input_prefix():
    template = yaml.safe_load(TEMPLATE.read_text())
    event = template["Resources"]["ReliabilityFunction"]["Properties"]["Events"]["InputUpload"]
    rules = event["Properties"]["Filter"]["S3Key"]["Rules"]
    assert {"Name": "prefix", "Value": "input/"} in rules


def test_example_parameters_contain_no_real_account_values():
    params = __import__("json").loads(PARAMETERS.read_text())
    model = params["Parameters"]["BedrockModelId"]
    assert "REPLACE_WITH" in model
