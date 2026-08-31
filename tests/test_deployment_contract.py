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
    assert "ReliabilityBucketPolicy" in resources
    assert "ReliabilityFunction" in resources
    assert "ReliabilityLogGroup" in resources
    assert "ProcessedMetricFilter" in resources
    assert "FailedMetricFilter" in resources
    assert "Dashboard" in resources


def test_s3_bucket_has_encryption_versioning_and_public_access_block():
    bucket = load_template()["Resources"]["ReliabilityBucket"]["Properties"]
    encryption = bucket["BucketEncryption"]["ServerSideEncryptionConfiguration"][0]["ServerSideEncryptionByDefault"]
    assert encryption["SSEAlgorithm"] == "AES256"
    assert encryption["BucketKeyEnabled"] is True
    assert bucket["VersioningConfiguration"] == {"Status": "Enabled"}
    assert bucket["PublicAccessBlockConfiguration"] == {
        "BlockPublicAcls": True,
        "BlockPublicPolicy": True,
        "IgnorePublicAcls": True,
        "RestrictPublicBuckets": True,
    }


def test_s3_bucket_denies_insecure_transport():
    policy = load_template()["Resources"]["ReliabilityBucketPolicy"]["Properties"]["PolicyDocument"]
    statement = policy["Statement"][0]
    assert statement["Effect"] == "Deny"
    assert statement["Action"] == "s3:*"
    assert statement["Condition"] == {"Bool": {"aws:SecureTransport": False}}


def test_lambda_uses_bounded_async_retries_and_failure_destination():
    config = load_template()["Resources"]["ReliabilityFunction"]["Properties"]["EventInvokeConfig"]
    assert config["MaximumEventAgeInSeconds"] == 3600
    assert config["MaximumRetryAttempts"] == 2
    assert config["DestinationConfig"]["OnFailure"] == {"Type": "SQS"}


def test_lambda_uses_structured_cloudwatch_logging():
    template = load_template()
    logging_config = template["Resources"]["ReliabilityFunction"]["Properties"]["LoggingConfig"]
    assert logging_config == {
        "LogFormat": "JSON",
        "ApplicationLogLevel": "INFO",
        "SystemLogLevel": "WARN",
    }


def test_lambda_has_bedrock_and_cloudwatch_permissions():
    template = load_template()
    policies = template["Resources"]["ReliabilityFunction"]["Properties"]["Policies"]
    bedrock_statements = policies[2]["Statement"]
    bedrock_actions = bedrock_statements[0]["Action"]
    assert "bedrock:InvokeModel" in bedrock_actions
    assert "bedrock:Converse" in bedrock_actions

    cloudwatch_statements = policies[3]["Statement"]
    assert cloudwatch_statements[0]["Action"] == ["cloudwatch:PutMetricData"]
    assert cloudwatch_statements[0]["Condition"] == {
        "StringEquals": {"cloudwatch:namespace": "AgenticDataReliability"}
    }


def test_s3_eventbridge_trigger_targets_input_prefix():
    template = load_template()
    bucket = template["Resources"]["ReliabilityBucket"]
    assert bucket["Properties"]["NotificationConfiguration"] == {
        "EventBridgeConfiguration": {"EventBridgeEnabled": True}
    }
    event = template["Resources"]["ReliabilityFunction"]["Properties"]["Events"]["InputUpload"]
    assert event["Type"] == "EventBridgeRule"
    pattern = event["Properties"]["Pattern"]
    assert pattern["source"] == ["aws.s3"]
    assert pattern["detail-type"] == ["Object Created"]
    assert pattern["detail"]["object"]["key"] == [{"prefix": "input/"}]


def test_observability_metrics_cover_processed_failed_and_duration():
    resources = load_template()["Resources"]

    processed = resources["ProcessedMetricFilter"]
    assert processed["Properties"]["FilterPattern"] == "dataset_processed"
    assert processed["Properties"]["MetricTransformations"][0]["MetricName"] == "DatasetsProcessed"

    failed = resources["FailedMetricFilter"]
    assert failed["Properties"]["FilterPattern"] == "dataset_processed failed"
    assert failed["Properties"]["MetricTransformations"][0]["MetricName"] == "DatasetsFailed"

    assert "DurationMetricFilter" not in resources

    dashboard = resources["Dashboard"]["Properties"]["DashboardBody"]
    assert "DatasetsProcessed" in dashboard
    assert "DatasetsFailed" in dashboard
    assert "ProcessingDurationMs" in dashboard


def test_example_parameters_contain_no_real_account_values():
    params = json.loads(PARAMETERS.read_text())
    model = params["Parameters"]["BedrockModelId"]
    assert "REPLACE_WITH" in model
