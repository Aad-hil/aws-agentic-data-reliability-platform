# AWS Execution Boundary — Phase 4.1

Phase 4.1 introduces the first AWS runtime boundary without moving agent orchestration into AWS yet.

## Flow

S3 upload to `input/`
→ S3 ObjectCreated event
→ Lambda
→ deterministic profiler/evaluator
→ JSON reliability report
→ S3 `reports/`

The Lambda deliberately stops after producing the deterministic report. Bedrock-powered agents remain behind the existing application layer and will be connected in the next phase.

## Why S3 + Lambda

- S3 provides durable, low-ops object storage for datasets and reports.
- Lambda gives us an event-driven execution boundary with no server management.
- The `input/` prefix prevents the Lambda from triggering itself when it writes to `reports/`.
- The Lambda uses an IAM policy scoped to the created bucket.

## Deployment

The infrastructure is defined in `infra/template.yaml` using AWS SAM. Deploying the template creates the bucket, event notification, Lambda, and scoped S3 permissions.

No AWS credentials, bucket names, or secrets are committed to the repository.
