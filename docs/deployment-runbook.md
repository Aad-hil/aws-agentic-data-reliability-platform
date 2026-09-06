# Deployment Runbook

## Prerequisites checklist

Before deploying, confirm:

- [ ] AWS CLI is authenticated to the target AWS account.
- [ ] AWS SAM CLI is installed.
- [ ] Python 3.12 is available locally.
- [ ] Target region is `us-east-1` (or a region where the selected Bedrock inference profile is available).
- [ ] Required Amazon Bedrock model/inference profile access is enabled in the target region.
- [ ] The deployment identity can create/update CloudFormation, Lambda, S3, IAM, CloudWatch Logs, CloudWatch Dashboard, EventBridge, and SQS resources required by `infra/template.yaml`.
- [ ] The sample input `data/sample/customers.csv` is available locally.
- [ ] Expected costs have been reviewed: Lambda/S3/EventBridge/CloudWatch/SQS usage plus Athena query/storage costs if the BI layer is used, and Bedrock inference charges for model calls. This repository does not claim a fixed AWS cost.
- [ ] No AWS credentials, secrets, or account-specific values are being added to source control.

Current validated deployment defaults are defined in `samconfig.toml`: stack `agentic-data-reliability`, region `us-east-1`, Bedrock inference profile `us.amazon.nova-2-lite-v1:0`, and 14-day log retention.

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

## 4. Local validation

Run the AWS-independent regression suite:

```bash
python -m pytest -q
```

The suite uses fakes for AWS/Bedrock boundaries and should pass without an AWS region or live model calls.

## 5. End-to-end smoke test

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

## 6. Failure-path verification

Upload a deliberately malformed CSV to a separate test key and verify:

- The record reaches the Lambda failure path.
- The Lambda invocation does not expose secrets or dataset contents in logs.
- A transient Bedrock failure is retried within the configured bound.
- The function does not automatically mutate source data.
- Repeated failures eventually reach the configured SQS failure destination.

## Test artifact cleanup

After validation, remove temporary E2E objects when they are no longer needed:

```bash
aws s3 rm s3://<bucket>/input/customers-e2e-003.csv
aws s3 rm s3://<bucket>/reports/customers-e2e-003.json
```

Keep the committed sample dataset under `data/sample/`.

## Teardown

For a temporary evaluation environment, delete the SAM stack after collecting required evidence:

```bash
sam delete --stack-name agentic-data-reliability --region us-east-1
```

Review retained resources before/after deletion. The Lambda log group is configured with `DeletionPolicy: Retain`, so remove retained logs explicitly only when their retention is no longer required.

## Rollback

Use CloudFormation/SAM stack update or rollback for infrastructure changes. For application-only changes, redeploy the previous known-good commit. Preserve the retained CloudWatch log group during rollback.

## Operational acceptance criteria

- SAM validation passes.
- SAM build passes.
- Local regression suite passes.
- Lambda is invokable.
- S3 input event reaches Lambda.
- A successful report is written to S3.
- CloudWatch logs contain correlated structured events.
- CloudWatch dashboard shows Lambda metrics.
- Failure paths are isolated and observable.
