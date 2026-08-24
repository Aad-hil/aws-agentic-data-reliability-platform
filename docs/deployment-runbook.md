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
sam validate --template-file infra/template.yaml
```

Expected result: the template is valid.

## 2. Build

```sam build --template-file infra/template.yaml```

Expected result: SAM builds the Lambda artifact without errors.

## 3. Deploy

```bash
sam deploy --guided --template-file infra/template.yaml
```

Set `BedrockModelId` to a model enabled in your target region. Do not commit generated configuration containing account-specific or secret values.

## 4. End-to-end smoke test

1. Use the deployed bucket output.
2. Upload `data/sample/customers.csv` under `input/customers.csv`.
3. Wait for the S3 event to invoke Lambda.
4. Confirm `reports/customers.json` is created.
5. Confirm the report contains reliability findings plus incident, RCA, and recommendation objects.
6. Open the CloudWatch dashboard and confirm invocation, error, and duration metrics.
7. Search the Lambda log group using the returned `request_id`.

## 5. Failure-path verification

Upload a deliberately malformed CSV to a separate test key and verify:

- The record appears in `failures`.
- The Lambda invocation does not expose secrets or dataset contents in logs.
- A transient Bedrock failure is retried within the configured bound.
- The function does not automatically mutate source data.

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
