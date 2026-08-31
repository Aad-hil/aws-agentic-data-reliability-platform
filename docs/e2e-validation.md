# AWS E2E Validation

## Purpose

This document records the live AWS validation checkpoint for the deployed reliability platform. It captures evidence from a real S3-triggered execution rather than relying only on unit tests or infrastructure deployment status.

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
- Runtime: Python 3.12
- Test case: intentionally faulty `mixed_issues.csv`
- Fresh E2E object: `input/customers-e2e-final-v2.csv`

## Evidence

The fresh execution produced a persisted reliability report with:

- status: `failed`
- score: `35`
- finding count: `5`
- severity counts: `4 error`, `1 warning`, `0 critical`, `0 info`

The report identified representative issues including a missing age value, invalid email, out-of-range age, invalid plan domain value, and schema drift.

CloudWatch datapoints from the fresh run:

| Metric | Dimension | Observed value |
|---|---|---:|
| `DatasetsProcessed` | none | `1` |
| `DatasetsFailed` | none | `1` |
| `ProcessingDurationMs` | `Dataset=customers-e2e-final-v2` | `9281 ms` average |

The processed and failed counters landed in the 15:45 UTC minute bucket. The duration metric was observed in the corresponding five-minute bucket.

## Observability design note

Dataset processing counters are emitted from CloudWatch Logs metric filters. The Lambda emits the processing event as structured JSON content in the log message, and the deployed metric filters match that representation. Processing duration is emitted directly with `PutMetricData` and uses the dataset name as a dimension.

The previous duration metric-filter approach was intentionally removed because CloudWatch metric-filter transformations require a valid numeric extraction and cannot safely treat the logged duration expression as a dynamic metric value. Direct `PutMetricData` is the simpler and more reliable implementation for duration telemetry.

## Validation outcome

**PASS.** The deployed AWS workflow was exercised with a fresh faulty dataset and produced both the expected reliability report and live operational metrics. This checkpoint is the evidence baseline for subsequent portfolio work.

## Reproduction outline

1. Build and validate the SAM template.
2. Deploy with `sam deploy`.
3. Upload an evaluation dataset to the bucket's `input/` prefix.
4. Wait for the EventBridge-triggered Lambda execution.
5. Confirm the report appears under `reports/`.
6. Query the CloudWatch metrics for the execution window.

Live validation is deliberately separate from normal CI because it invokes AWS services and Amazon Bedrock and therefore introduces credentials, latency, cost, and model variance.
