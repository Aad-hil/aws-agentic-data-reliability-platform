# AWS E2E Validation

## Purpose

This document records the live AWS validation checkpoints for the deployed reliability platform. It captures evidence from real S3-triggered executions rather than relying only on unit tests or infrastructure deployment status.

## Validated flow

```text
S3 input/*.csv
    ↓
EventBridge ObjectCreated
    ↓
AWS Lambda
    ↓
Deterministic reliability engine
    ↓
Detection → RCA → Recommendation agents
    ↓
Amazon Bedrock
    ↓
S3 reports/*.json
    ↓
CloudWatch Logs + Metrics
```

## Environment

- CloudFormation stack: `agentic-data-reliability`
- Region: `us-east-1`
- Lambda runtime: Python 3.12
- Lambda memory: 512 MB
- Test case: intentionally faulty `mixed_issues.csv`
- Representative dataset size: 3 rows

## Final repeated benchmark evidence

After the resilience hardening deployment, the same representative dataset was uploaded three times under unique input keys:

| Run | Input | Report | ProcessingDurationMs |
|---|---|---|---:|
| 1 | `benchmark-run-1c.csv` | `benchmark-run-1c.json` | `9055 ms` |
| 2 | `benchmark-run-2.csv` | `benchmark-run-2.json` | `10779 ms` |
| 3 | `benchmark-run-3.csv` | `benchmark-run-3.json` | `8067 ms` |

All three reports were observed in the S3 `reports/` prefix. The three duration observations average **9300 ms**.

These runs provide stronger evidence than the earlier single-run checkpoint because the same workload was exercised repeatedly after deployment. The benchmark is still intentionally small and should not be presented as a production SLA or statistically significant load test.

## Earlier AWS validation checkpoint

An earlier fresh run of `customers-e2e-final-v2` recorded:

- `DatasetsProcessed = 1`
- `DatasetsFailed = 1`
- `ProcessingDurationMs = 9281 ms` average

The persisted report had status `failed`, score `35`, and five findings (four errors and one warning). This remains useful as evidence of the original data-quality and observability path.

## Observability design

Dataset processing counters are emitted through CloudWatch Logs metric filters. The Lambda emits structured JSON content containing the processing event, and the deployed filters match that representation. Processing duration is emitted directly with `PutMetricData` using the dataset name as a dimension.

The duration metric-filter approach was removed because direct `PutMetricData` gives the application explicit control over the numeric telemetry and avoids treating a dynamic duration value as a metric-filter transformation expression.

## Resilience validation

Phase 6.4 introduced explicit failure boundaries: transient Bedrock failures use bounded retries, malformed recommendation output gets one repair attempt, Lambda surfaces record failures as invocation errors, asynchronous retries are capped, and exhausted events have an SQS failure destination.

The benchmark runs above demonstrate successful processing after that deployment. Failure-path behavior is additionally covered by static Lambda and deployment-contract tests in CI; no destructive remediation is enabled.

## Validation outcome

**PASS.** The deployed AWS workflow has been exercised repeatedly with a representative faulty dataset. Reports are persisted, CloudWatch duration telemetry is recorded, and the platform has explicit bounded failure/retry behavior.

## Reproduction outline

1. Build and validate the SAM template.
2. Deploy with `sam deploy`.
3. Upload an evaluation dataset to the bucket's `input/` prefix using a unique key.
4. Wait for the EventBridge-triggered Lambda execution.
5. Confirm the corresponding report appears under `reports/`.
6. Query the CloudWatch metrics for the execution window.
7. Repeat with additional representative datasets for a stronger performance sample.

Live validation is deliberately separate from normal CI because it invokes AWS services and Amazon Bedrock and therefore introduces credentials, latency, cost, and model variance.
