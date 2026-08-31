# Project Plan

## Completed

### Phase 0 — Foundation
- [x] GitHub repository, README, license, ignore rules, environment template
- [x] Architecture and project plan

### Phase 1 — Data foundation
- [x] Realistic sample dataset
- [x] Initial data model and reliability scenarios

### Phase 2 — Reliability engine
- [x] Profiling
- [x] Deterministic checks and findings
- [x] Evaluation and report generation
- [x] Unit tests

### Phase 3 — Agentic reasoning
- [x] Typed contracts
- [x] Bedrock adapter
- [x] Detection, RCA, and Recommendation agents
- [x] Sequential orchestrator
- [x] Local end-to-end workflow

### Phase 4 — AWS runtime
- [x] 4.1 S3 + Lambda execution boundary
- [x] 4.2 Lambda + Bedrock agent workflow
- [x] 4.3 Error handling, retry boundaries, and structured logging
- [x] 4.4 CloudWatch observability and operational metrics
- [x] 4.5 Deployment validation and runbook
- [x] Phase 4 E2E validation: S3 → EventBridge → Detection → RCA → Recommendation → Bedrock → S3 report

**Phase 4 checkpoint:** completed against the deployed `agentic-data-reliability` stack in `us-east-1`. A controlled E2E run processed a faulty dataset and produced a persisted reliability report.

### Phase 5 — Evaluation and portfolio hardening
- [x] Representative reliability cases
- [x] Agent output regression/evaluation suite
- [x] Live Bedrock evaluation harness
- [x] CloudWatch observability dashboard and operational metrics
- [x] Deployment and troubleshooting validation
- [x] Fresh AWS E2E validation with live metric datapoints
- [x] Portfolio documentation and evidence checkpoint

**Phase 5 checkpoint:** completed on the deployed `agentic-data-reliability` stack in `us-east-1`. A fresh intentionally faulty dataset produced `DatasetsProcessed=1`, `DatasetsFailed=1`, and `ProcessingDurationMs=9281 ms`. The persisted report had status `failed`, score `35`, and five findings (four errors and one warning).

### Phase 6 — Portfolio performance and production-readiness
- [x] 6.1 Cost and latency evidence baseline
- [x] 6.2 Repeated performance benchmark across representative datasets
- [x] 6.3 Security and IAM review
- [x] 6.4 Failure/retry and operational resilience review
- [x] 6.5 Final portfolio walkthrough and architecture evidence

**Phase 6.1/6.2 checkpoint:** repeated live AWS executions of the representative three-row `mixed_issues.csv` dataset produced `ProcessingDurationMs` values of `9055 ms`, `10779 ms`, and `8067 ms`. The observed range was 8.1–10.8 seconds with a mean of approximately 9.3 seconds. These are evidence measurements, not a production SLA. No single-run dollar estimate is claimed.

**Phase 6.3 checkpoint:** completed a security/IAM review and hardened the S3 boundary with AES-256 encryption + Bucket Key, versioning, all four S3 Public Access Block controls, and an explicit deny for non-TLS S3 requests. Lambda permissions remain service/action scoped; CloudWatch metric writes are restricted to the project namespace. Bedrock inference remains the only documented IAM limitation because the configurable inference-profile/model resource is currently represented as `*` for deployment portability. Static contract tests cover the security controls.

**Phase 6.4 checkpoint:** completed the failure/retry and operational resilience review. Bedrock transient failures retain bounded exponential-backoff retries; malformed model output gets one repair attempt; Lambda surfaces record failures as invocation errors instead of silently acknowledging them; asynchronous Lambda retries are capped at two attempts within one hour and exhausted events are routed to an automatically provisioned SQS failure destination. The remaining production hardening item is durable idempotency for multi-record/replayed events.

**Phase 6.5 checkpoint:** finalized the portfolio evidence layer. README and supporting documentation now reflect the completed phases, repeated AWS benchmark evidence, security posture, resilience model, and known production hardening limitation. The repository presents a consistent architecture narrative from deterministic reliability evidence through Bedrock-powered interpretation and bounded AWS operations.

## Scope guardrails

Use deterministic logic for facts, model inference for interpretation, and human review for consequential remediation. Add an AWS service or agent only when it demonstrates a concrete architectural capability.
