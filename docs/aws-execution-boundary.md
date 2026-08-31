# AWS Execution Boundary — Phase 4

The AWS runtime provides the production-style execution boundary for the reliability platform. The deployed workflow is event-driven, serverless, and keeps deterministic evidence generation separate from model-based interpretation.

## Flow

```text
S3 upload to input/
→ EventBridge ObjectCreated
→ Lambda
→ deterministic profiler/evaluator
→ Detection / RCA / Recommendation agents
→ Amazon Bedrock
→ JSON reliability report
→ S3 reports/
→ CloudWatch Logs + Metrics
```

The Lambda is the orchestration boundary. Deterministic checks establish the facts first; Bedrock-powered agents interpret those facts and produce bounded, advisory recommendations. Automatic destructive remediation remains disabled.

## Why S3 + EventBridge + Lambda

- S3 provides durable, low-ops object storage for datasets and reports.
- EventBridge provides an explicit event-routing boundary for S3 ObjectCreated events.
- Lambda provides event-driven execution with no server management.
- The `input/` prefix prevents the Lambda from triggering itself when it writes to `reports/`.
- The Lambda uses IAM permissions scoped to the deployed resources.
- CloudWatch provides logs, operational counters, and processing-duration telemetry.

## Failure and retry boundary

The runtime uses separate retry layers for different failure classes:

1. The Bedrock adapter retries known transient service failures with bounded exponential backoff and jitter.
2. The recommendation agent performs one repair attempt for malformed or schema-invalid model output.
3. The Lambda handler raises when an input record fails, so asynchronous Lambda processing does not silently acknowledge failed work.
4. `EventInvokeConfig` limits Lambda asynchronous retries to two attempts and one hour of event age.
5. After retries are exhausted, SAM's SQS failure destination captures the failed event for operational investigation or controlled reprocessing.

This prevents both silent event loss and unbounded retry storms.

## Observability

The deployed stack exposes:

- `DatasetsProcessed` — CloudWatch Logs metric filter
- `DatasetsFailed` — CloudWatch Logs metric filter
- `ProcessingDurationMs` — direct `PutMetricData` publication with a `Dataset` dimension
- Native Lambda `Invocations` and `Errors` metrics for runtime health

The duration metric is deliberately published directly rather than extracted through a metric-filter transformation. This avoids treating a dynamic log value as a metric transformation expression and gives the application explicit control over the numeric telemetry.

## Live validation

The deployed `agentic-data-reliability` stack in `us-east-1` was validated with a fresh intentionally faulty evaluation dataset. The E2E run produced a persisted reliability report and these CloudWatch datapoints:

- `DatasetsProcessed = 1`
- `DatasetsFailed = 1`
- `ProcessingDurationMs = 9281 ms` average for the tested dataset

See [E2E validation](e2e-validation.md) for the complete evidence checkpoint.

## Deployment

The infrastructure is defined in `infra/template.yaml` using AWS SAM. Deploying the template creates the bucket, EventBridge rule, Lambda, IAM role, CloudWatch log group, metric filters, dashboard, and Lambda failure destination.

No AWS credentials, bucket names, or secrets are committed to the repository.
