# Failure, Retry, and Operational Resilience Review — Phase 6.4

## Scope

This checkpoint reviews how failures move through the deployed S3 → EventBridge → Lambda → Bedrock workflow. The goal is bounded recovery, visible failure evidence, and no silent loss of input events.

## Failure boundaries

| Failure | Handling | Outcome |
|---|---|---|
| Bedrock throttling / service unavailable | Bedrock adapter retries with bounded exponential backoff | Recoverable transient failure |
| Bedrock malformed JSON | Recommendation agent performs one schema-repair attempt | Controlled model-output recovery |
| Bedrock still invalid after repair | Exception propagates from the agent workflow | Lambda invocation fails and enters async retry policy |
| S3 read/write failure | Lambda records structured failure and raises | Lambda async retry policy applies |
| Unexpected application exception | Structured error log + raised exception | Lambda async retry policy applies |
| Repeated Lambda failure | Lambda retries are capped | Event is sent to the generated SQS failure destination |
| Invalid/non-input object | Lambda skips the record | No retry loop |

## Lambda retry boundary

The Lambda handler previously collected record failures and returned a successful invocation response. That behavior is unsafe for an asynchronous event-driven system because the upstream service can interpret the invocation as successful even though the dataset was not processed.

Phase 6.4 changes the boundary: after all records are evaluated, any record failure is raised as an invocation-level error. This lets the Lambda asynchronous retry mechanism see the failure instead of silently acknowledging it.

The SAM configuration now uses:

- Maximum event age: **3600 seconds**
- Maximum retry attempts: **2**
- On-failure destination: **SQS** (automatically provisioned by SAM)

This is intentionally bounded. The system should not retry indefinitely when the underlying input or model response is permanently invalid.

## Model-level retry boundary

The Bedrock adapter separately retries only known transient service failures such as throttling, service unavailable, and internal service errors. The existing default is three attempts with exponential backoff and jitter.

Model-output failures are handled differently: malformed JSON is a contract violation rather than a transport failure. The recommendation agent gets one explicit repair attempt and then fails closed.

## Idempotency consideration

Retries can cause the same S3 object to be processed more than once. The current portfolio implementation writes reports using a deterministic `reports/<dataset>.json` key, so repeated processing replaces the same report rather than creating unbounded duplicate objects.

A production multi-record workload would need stronger idempotency controls, such as a request/object-version key stored in DynamoDB or another durable idempotency store. That is deliberately outside the current minimal portfolio scope.

## Observability

Failures are emitted as structured `dataset_failed` log events and successful processing emits `dataset_processed`. Lambda's native `Errors` metric can therefore be correlated with application failure logs and the existing `DatasetsFailed` metric.

The failure destination should be treated as an operational queue for investigation/reprocessing, not as an automatic remediation path. Destructive data mutation remains disabled.

## Verification

Static CI tests verify the retry contract without AWS credentials:

```bash
python -m pytest tests/test_lambda_handler.py tests/test_deployment_contract.py -q
```

The deployment template is also validated with:

```bash
sam validate --template-file infra/template.yaml --lint
```

## Portfolio conclusion

**PASS.** The platform now has explicit failure boundaries: transient Bedrock failures retry locally, invalid model output gets one bounded repair attempt, Lambda application failures are surfaced to the asynchronous runtime, retries are capped, and exhausted failures have an SQS destination for operational follow-up.

The remaining production hardening item is durable idempotency for multi-record/replayed events. That is documented rather than hidden.
