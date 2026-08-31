# Performance and Cost Evidence

## Phase 6.1 — Cost and latency evidence

This checkpoint records measurements from a real AWS execution of the deployed platform. The goal is to establish an evidence baseline before making performance or cost optimizations.

## Live measurement

Environment:

- Stack: `agentic-data-reliability`
- Region: `us-east-1`
- Lambda runtime: Python 3.12
- Lambda memory: 512 MB
- Lambda timeout: 60 seconds
- Model: `us.amazon.nova-2-lite-v1:0`
- Dataset: `customers-e2e-final-v2`
- Dataset size: 3 rows

Observed CloudWatch metric:

| Metric | Dimension | Observed value |
|---|---|---:|
| `ProcessingDurationMs` | `Dataset=customers-e2e-final-v2` | `9281 ms` average |
| `DatasetsProcessed` | none | `1` |
| `DatasetsFailed` | none | `1` |

The duration metric represents the Lambda-side end-to-end processing interval for the dataset, including deterministic analysis, agent orchestration, report persistence, and metric publication.

## Cost accounting

This project intentionally does **not** hard-code a dollar amount from a single run. Actual cost depends on the AWS account's pricing, model token usage, request volume, Lambda memory duration, and other account-level factors.

The platform already exposes the main runtime measurement needed for ongoing analysis: processing duration. Lambda configuration is also explicit in `infra/template.yaml`, making the compute-cost assumptions reviewable.

For Bedrock, token-level usage should be captured from AWS billing/usage data when a larger benchmark is performed. A single three-row E2E run is useful as a latency proof but is not statistically meaningful as a production cost estimate.

## Engineering interpretation

The current result is a **baseline, not an optimization target**. At roughly 9.3 seconds for a deliberately small dataset, the dominant latency is expected to be the model-backed workflow rather than CSV parsing or deterministic checks. The next useful benchmark should run multiple representative datasets and compare latency and model usage across clean, missing-value, invalid-value, and mixed-issue cases.

No architectural optimization is justified from one observation. Keeping the workflow simple is preferred until repeated measurements demonstrate a bottleneck.

## Reproduction

After a fresh E2E execution, query the duration metric with the dataset dimension:

```bash
aws cloudwatch get-metric-statistics \
  --namespace AgenticDataReliability \
  --metric-name ProcessingDurationMs \
  --dimensions Name=Dataset,Value=<dataset-name> \
  --start-time <start> \
  --end-time <end> \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

The corresponding processed/failed counters can be queried from the `DatasetsProcessed` and `DatasetsFailed` metrics.

## Portfolio takeaway

The project now demonstrates measured AWS runtime behavior rather than only theoretical architecture: a live dataset was processed in approximately 9.3 seconds, the resulting reliability report was persisted, and CloudWatch recorded the processing and outcome metrics.
