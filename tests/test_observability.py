from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "infra" / "template.yaml"


class CloudFormationLoader(yaml.SafeLoader):
    pass


def _construct_intrinsic(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


CloudFormationLoader.add_multi_constructor("!", _construct_intrinsic)


def load_template():
    return yaml.load(TEMPLATE.read_text(), Loader=CloudFormationLoader)


def test_observability_metric_filters_exist():
    resources = load_template()["Resources"]
    assert {
        "ProcessedMetricFilter",
        "FailedMetricFilter",
        "DurationMetricFilter",
    }.issubset(resources)


def test_observability_metric_namespace_and_names():
    resources = load_template()["Resources"]
    expected = {
        "ProcessedMetricFilter": "DatasetsProcessed",
        "FailedMetricFilter": "DatasetsFailed",
        "DurationMetricFilter": "ProcessingDurationMs",
    }
    for resource_name, metric_name in expected.items():
        transform = resources[resource_name]["Properties"]["MetricTransformations"][0]
        assert transform["MetricNamespace"] == "AgenticDataReliability"
        assert transform["MetricName"] == metric_name


def test_dashboard_contains_agentic_reliability_metrics():
    dashboard = load_template()["Resources"]["Dashboard"]["Properties"]["DashboardBody"]
    assert "AgenticDataReliability" in dashboard
    assert "DatasetsProcessed" in dashboard
    assert "DatasetsFailed" in dashboard
    assert "ProcessingDurationMs" in dashboard
