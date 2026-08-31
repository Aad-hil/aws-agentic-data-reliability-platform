# Performance and Cost Evidence

## Phase 6.1 / 6.2 — Cost and latency evidence

This checkpoint records measurements from real AWS executions of the deployed platform. The goal is to establish a small but reproducible performance baseline before making optimization claims.

## Environment

- CloudFormation stack: `agentic-data-reliability`
- Region: `us-east-1`
- Lambda runtime: Python 3.12
- Lambda memory: 512 MB
- Lambda timeout: 60 seconds
- Bedrock model: `us.amazon.nova-2-lite-v1:0`
- Evaluation dataset: `data/evaluation/mixed_issues.csv`
- Dataset size: 3 rows

## Repeated live benchmark

Three fresh S3-triggered executions of the same representative faulty dataset were observed after deployment of the hardened runtime:

| Run | Input object | Report | ProcessingDurationMs | Outcome |
|---|---|---|---:|---|
| 1 | `benchmark-run-1c.csv` | persisted | `9055 ms` | completed |
| 2 | `benchmark-run-2.csv` | persisted | `10779 ms` | completed |
| 3 | `benchmark-run-3.csv` | persisted | `8067 ms` | completed |

The three observed durations have a simple mean of **9300 ms (9.3 seconds)**. The spread is approximately **2.7 seconds** from the fastest to slowest run, demonstrating why a single execution should not be treated as an SLA.

The benchmark is intentionally small. It establishes repeatability and operational evidence, not statistical production performance.

## What the benchmark proves

- The same representative reliability case can be executed repeatedly through the live AWS path.
- Reliability reports are persisted to the S3 `reports/` prefix for each run.
- Processing duration is emitted as a dataset-dimensioned CloudWatch metric.
- Runtime latency remains in the same general ~8–11 second range across the three observed runs.
- The model-backed workflow is the likely dominant latency component for this small dataset; deterministic CSV processing is unlikely to explain the full end-to-end duration.

## Cost accounting

This project intentionally does **not** claim a dollar cost from these runs. Actual cost depends on Bedrock input/output tokens, model pricing, request volume, Lambda memory-duration, S3 requests/storage, CloudWatch usage, and account-level pricing.

The benchmark therefore records latency and operational outcomes while avoiding a fabricated cost estimate. A production cost study should correlate Bedrock usage/billing data with a larger workload and include clean, faulty, and mixed-issue datasets.

## Engineering interpretation

The repeated benchmark is sufficient to establish a portfolio-level baseline but not to justify optimization. The observed variation is expected for a model-backed workflow and may reflect model latency, service scheduling, network/service conditions, and other runtime variance.

The current architecture should remain intentionally simple. Optimization should be driven by additional measurements such as token usage, p50/p95 latency, cold-start behavior, and per-agent timing if those become relevant.

## Reproduction

Upload the representative dataset under a unique input key:

```bash
aws s3 cp data/evaluation/mixed_issues.csv \
  s3://<reliability-bucket>/input/<run-name>.csv \
  --region us-east-1
```

Confirm the report:

```bash
aws s3 ls \
  s3://<reliability-bucket>/reports/<run-name>.json \
  --region us-east-1
```

Query the duration metric with the dataset dimension:

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

The corresponding processed/failed counters can be queried from `DatasetsProcessed` and `DatasetsFailed`.

## Portfolio takeaway

The platform now has a measured repeated AWS baseline rather than a single latency anecdote: three live executions of the same representative dataset produced persisted reports and observed processing durations of **9.055 s, 10.779 s, and 8.067 s**, averaging **9.3 s**. This is enough evidence to describe current behavior honestly while leaving further optimization to a future, larger benchmark.
