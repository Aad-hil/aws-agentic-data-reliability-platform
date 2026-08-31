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
- [x] Phase 4 E2E validation: S3 → EventBridge → Lambda → Detection → RCA → Recommendation → Bedrock → S3 report

### Phase 5 — Evaluation and portfolio hardening
- [x] Representative reliability cases
- [x] Agent output regression/evaluation suite
- [x] Live Bedrock evaluation harness
- [x] CloudWatch observability dashboard and operational metrics
- [x] Deployment and troubleshooting validation
- [x] Fresh AWS E2E validation with live metric datapoints
- [x] Portfolio documentation and evidence checkpoint

### Phase 6 — Portfolio performance and production-readiness
- [x] 6.1 Cost and latency evidence baseline
- [x] 6.2 Repeated performance benchmark across representative datasets
- [x] 6.3 Security and IAM review
- [x] 6.4 Failure/retry and operational resilience review
- [x] 6.5 Final portfolio walkthrough and architecture evidence

## Phase 6 checkpoints

**6.1 / 6.2 — Performance evidence:** three live executions of the same three-row representative faulty dataset recorded `ProcessingDurationMs` values of `9055 ms`, `10779 ms`, and `8067 ms`, averaging **9300 ms**. Each run produced a persisted S3 report. This establishes a repeatable portfolio baseline without claiming an SLA or fabricated dollar cost.

**6.3 — Security/IAM:** S3 encryption + Bucket Key, versioning, all four Public Access Block controls, and an explicit non-TLS deny are enabled. Lambda S3 permissions and CloudWatch metric writes are scoped; Bedrock inference is restricted to `InvokeModel`/`Converse`. The configurable Bedrock resource wildcard remains a documented portability trade-off.

**6.4 — Resilience:** transient Bedrock failures retain bounded exponential-backoff retries; malformed model output gets one repair attempt; Lambda surfaces record failures as invocation errors; asynchronous retries are capped at two attempts within one hour; exhausted failures are routed to an SQS failure destination. Durable idempotency for multi-record/replayed events remains future hardening.

**6.5 — Portfolio walkthrough and evidence:** documentation now reflects the actual deployed architecture, repeated AWS benchmark, security posture, resilience boundaries, verification commands, and known limitations. The repository is ready for a final portfolio review rather than another architectural expansion.

## Remaining production hardening

The project intentionally stops short of adding infrastructure without a demonstrated need. The main documented future improvement is durable idempotency for multi-record/replayed events, potentially using a request/object-version key in DynamoDB or another durable store.

## Scope guardrails

Use deterministic logic for facts, model inference for interpretation, and human review for consequential remediation. Add an AWS service or agent only when it demonstrates a concrete architectural capability.
