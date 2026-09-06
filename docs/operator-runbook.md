# Operator Runbook

This runbook covers the operational failure path for the portfolio-scale AWS Agentic Data Reliability Platform. It is intentionally conservative: failed events are investigated before replay, source data is not automatically mutated, and replay safety is not claimed as durable idempotency.

## Operational flow

```text
S3 input → EventBridge → Lambda → reliability/agents → S3 report
                                  |
                                  +-- exhausted async failures → SQS
                                  |
                                  +-- logs + metrics → CloudWatch
```

## 1. Detect an incident

Use the CloudWatch dashboard and Lambda logs to identify:

- `DatasetsFailed` increasing.
- Lambda `Errors` increasing.
- Processing duration materially above the documented benchmark baseline.
- Missing expected reports for an uploaded input.
- Messages accumulating in the Lambda failure destination SQS queue.

The documented benchmark mean is approximately 9.3 seconds for the validated representative case; it is **not** a production latency SLA. Investigate sustained or workload-specific degradation rather than treating one slow invocation as an incident by itself.

## 2. Investigate SQS failures

When an event reaches the SQS failure destination:

1. Record the message/event metadata and time observed.
2. Identify the source S3 object and the Lambda request context when available.
3. Search CloudWatch Logs using `request_id` and the relevant object key.
4. Determine whether the failure was caused by malformed input, an application defect, an AWS service/transient dependency, or configuration/model-access issues.
5. Do **not** modify the source dataset while investigating.
6. Preserve the failed event until the cause and replay decision are documented.

The Lambda asynchronous retry boundary is configured for a maximum event age of 1 hour and 2 retries. Exhausted failures are routed to SQS. fileciteturn176file0L2-L2

## 3. Replay safety

Replay is **not guaranteed idempotent** for arbitrary multi-record/replayed events. Treat every replay as a new processing attempt.

Before replaying:

- Confirm the original source object is unchanged.
- Check whether a report already exists for the event/object.
- Confirm whether downstream consumers can tolerate a repeated report.
- Prefer replaying a controlled copy or isolated test object when investigating application behavior.
- Record the original request ID and the replay request ID.

Do not claim that S3 versioning or deterministic report naming provides full distributed idempotency; those controls aid recovery but do not replace an explicit idempotency store.

## 4. Report retention

Reports are written under the S3 `reports/` prefix. The repository does not impose a fixed report-retention lifecycle policy in the application.

For a temporary portfolio/demo environment:

- Keep only evidence needed for validation and screenshots.
- Remove temporary test inputs/reports after the walkthrough.
- Review S3 storage growth before leaving the environment deployed.

For a production deployment, define a separate S3 lifecycle/retention policy based on regulatory, audit, and operational requirements before enabling long-term ingestion.

## 5. Alert thresholds

The current implementation provides CloudWatch metrics for processed/failed datasets, Lambda invocations/errors, and processing duration. It does not ship a production alerting policy with validated thresholds.

For a production adaptation, establish thresholds from workload baselines. Reasonable starting signals to evaluate are:

| Signal | Suggested investigation trigger |
|---|---|
| `DatasetsFailed` | Any unexpected increase above the normal baseline |
| Lambda `Errors` | Any sustained non-zero error rate |
| SQS failure destination | Any unexpected message arrival |
| Processing duration | Sustained deviation from the workload baseline |
| Missing reports | An expected report not produced within the workload's agreed processing window |

These are operational starting points, **not validated production SLOs**.

## 6. Incident escalation

Escalate in this order:

1. **Input/configuration issue:** data owner or pipeline owner.
2. **Application/reliability engine issue:** application owner.
3. **Bedrock/model access or AWS dependency issue:** AWS/platform owner.
4. **Repeated SQS failures or data-loss risk:** platform/application owner with the data owner involved.
5. **Security/IAM concern:** security owner before replay or permission changes.

For every escalated incident, preserve the request ID, source object key, failure reason, timestamps, relevant CloudWatch evidence, and replay decision.

## 7. Recovery principles

- Fix the cause before replaying the event.
- Replay only after assessing duplicate-processing consequences.
- Keep automatic destructive remediation disabled unless a separately reviewed production design introduces explicit authorization, auditability, and rollback controls.
- Validate the recovered path with a representative test object before resuming normal ingestion.
- Record the incident outcome and any required follow-up hardening.

## 8. Teardown after a portfolio demo

If the environment is temporary, follow `docs/deployment-runbook.md` for artifact cleanup and SAM teardown. Review retained CloudWatch logs before final account cleanup.
