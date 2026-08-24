# Observability — Phase 4.4

## Signals

The runtime now emits structured JSON application logs with:

- event name
- UTC timestamp
- Lambda request ID
- S3 bucket/key
- dataset name
- reliability status
- processing duration
- failure type

AWS Lambda's native metrics provide invocation count, errors, throttles, duration, and concurrency.

## CloudWatch

The SAM stack creates a retained Lambda log group with configurable retention and a CloudWatch dashboard for:

- Invocations
- Errors
- Duration

Set `LogRetentionDays` during deployment; the default is 14 days.

## Operational workflow

1. Start with the CloudWatch dashboard for health.
2. Check Lambda Errors and Duration for regressions.
3. Search the log group by `request_id` to trace an invocation.
4. Search `event=dataset_failed` for record-level failures.
5. Correlate Bedrock failures with the request ID and retry logs.

## Security

Logs intentionally record identifiers needed for operational debugging but do not log CSV contents, prompts, model responses, credentials, or secrets.
