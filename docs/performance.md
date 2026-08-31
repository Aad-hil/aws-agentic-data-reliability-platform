# Performance and Cost Evidence

## Phase 6.1 / 6.2 — Cost and latency evidence

This checkpoint records measured behavior from repeated AWS executions of the deployed platform. The goal is to establish a realistic latency baseline without inventing a production SLA or single-run cost estimate.

## Environment

- Stack: `agentic-data-reliability`
- Region: `us-east-1`
- Lambda runtime: Python 3.12
- Lambda memory: 512 MB
- Lambda timeout: 60 seconds
- Model: `us.amazon.nova-2-lite-v1:0`
- Dataset: `data/evaluation/mixed_issues.csv`
- Dataset size: 3 rows

## Repeated benchmark

Three fresh uploads of the same representative mixed-issue dataset were executed after the final resilience changes.

| Run | Input object | Report | `ProcessingDurationMs` |
|---|---|---|---:|
| 1 | `benchmark-run-1c.csv` | `benchmark-run-1c.json` | 9055 ms |
| 2 | `benchmark-run-2.csv` | `benchmark-run-2.json` | 10779 ms |
| 3 | `benchmark-run-3.csv` | `benchmark-run-3.json` | 8067 ms |

Observed range: **8067–10779 ms**.

Mean latency across the three observed runs: **9300 ms (9.3 s)**.

The measurements are CloudWatch `ProcessingDurationMs` averages for each dataset dimension and represent the Lambda-side end-to-end processing interval, including deterministic analysis, agent orchestration, Bedrock inference, report persistence, and metric publication.

## Interpretation

The repeated benchmark is more useful than the earlier single-run baseline because it shows normal run-to-run variance. The observed spread is approximately 2.7 seconds, so the platform should not claim a fixed latency guarantee from this small sample.

The workflow remains intentionally simple. The evidence does not yet justify architectural optimization. For a production workload, the next benchmark would increase sample count and dataset size and capture Bedrock token usage alongside Lambda duration.

## Outcome metrics

The benchmark also confirmed that CloudWatch outcome telemetry is operational. The earlier fresh E2E validation recorded `DatasetsProcessed=1` and `DatasetsFailed=1` for an intentionally faulty dataset, and the final benchmark runs produced persisted reports in S3.

A failed reliability report is not equivalent to a failed platform execution: the dataset can be successfully processed while the deterministic reliability assessment correctly reports data-quality failures. Operational success/failure should therefore be interpreted using both the report status and Lambda/application telemetry.

## Cost accounting

This project intentionally does **not** hard-code a dollar amount from these runs. Actual cost depends on account pricing, Bedrock token usage, request volume, Lambda memory duration, and other account-level factors.

The current benchmark establishes latency evidence only. A meaningful cost baseline should use AWS billing/usage data and a larger representative workload rather than extrapolating from three small model-backed executions.

## Reproduction

After each fresh E2E execution, query the duration metric with the dataset dimension:

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

**PASS.** The platform now has repeated live AWS latency evidence rather than a single observation. Three representative executions completed in 8.1–10.8 seconds, with a mean of approximately 9.3 seconds. The result is presented as an evidence baseline, not a production SLA or fabricated cost estimate.
