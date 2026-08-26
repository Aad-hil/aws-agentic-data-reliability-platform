# Deployment Runbook

## Prerequisites

- AWS CLI authenticated to the target account.
- AWS SAM CLI installed.
- Python 3.12 available locally.
- A Bedrock model enabled in the deployment region.
- Permissions to create CloudFormation, Lambda, S3, IAM, CloudWatch Logs, and CloudWatch Dashboard resources.

## 1. Validate

From the repository root:

```bash
sam validate --template-file infra/template.yaml --lint
```

Expected result: the template is valid and linting passes.

## 2. Build

```bash
sam build --template-file infra/template.yaml
```

Expected result: SAM builds the Lambda artifact without errors.

## 3. Deploy

```bash
sam deploy
```

The checked-in `samconfig.toml` contains the validated deployment defaults. Keep account-specific or secret values out of source control.

Current validated deployment:
- Stack: `agentic-data-reliability`
- Region: `us-east-1`
- Bedrock inference profile: `us.amazon.nova-2-lite-v1:0`
- Log retention: 14 days

## 4. End-to-end smoke test

1. Use the deployed bucket output.
2. Upload `data/sample/customers.csv` under a fresh `input/` test key.
3. Wait for the S3 EventBridge rule to invoke Lambda.
4. Confirm the Lambda log contains `invocation_started` and `invocation_completed` with `failures: 0`.
5. Confirm a corresponding report is created under `reports/`.
6. Confirm the report contains deterministic reliability findings plus incident, RCA, and recommendation objects.
7. Open the CloudWatch dashboard and confirm invocation, error, and duration metrics.
8. Search the Lambda log group using the returned `request_id`.

### Validated E2E evidence

The Phase 4 checkpoint was validated with `input/customers-e2e-003.csv`:

- Lambda: `processed: 1`, `failures: 0`
- Report: `reports/customers-e2e-003.json`
- Dataset: 50 rows, 8 columns
- Reliability score: 35/100
- Findings: 5 (4 errors, 1 warning)
- Detection, RCA, and Recommendation objects present
- Automatic mutation disabled

## 5. Failure-path verification

Upload a deliberately malformed CSV to a separate test key and verify:

- The record appears in `failures`.
- The Lambda invocation does not expose secrets or dataset contents in logs.
- A transient Bedrock failure is retried within the configured bound.
- The function does not automatically mutate source data.

## Test artifact cleanup

After validation, remove temporary E2E objects when they are no longer needed:

```bash
aws s3 rm s3://<bucket>/input/customers-e2e-003.csv
aws s3 rm s3://<bucket>/reports/customers-e2e-003.json
```

Keep the committed sample dataset under `data/sample/`.

## Rollback

Use CloudFormation/SAM stack update or rollback for infrastructure changes. For application-only changes, redeploy the previous known-good commit. Preserve the retained CloudWatch log group during rollback.

## Operational acceptance criteria

- SAM validation passes.
- SAM build passes.
- Lambda is invokable.
- S3 input event reaches Lambda.
- A successful report is written to S3.
- CloudWatch logs contain correlated structured events.
- CloudWatch dashboard shows Lambda metrics.
- Failure paths are isolated and observable.
