# AWS Agentic Data Reliability Platform

> Evidence-first, AWS-native multi-agent system for detecting data reliability issues, investigating likely root causes, and producing safe remediation recommendations.

[![CI](https://github.com/Aad-hil/aws-agentic-data-reliability-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Aad-hil/aws-agentic-data-reliability-platform/actions/workflows/ci.yml)

## Architecture

```text
S3 input/*.csv
      | ObjectCreated
      v
Amazon EventBridge
      |
      v
AWS Lambda
      |
      v
Deterministic Reliability Engine
(profile -> rules -> evaluate -> report)
      |
      v
Multi-Agent Orchestrator
      |
      +--> Detection Agent
      +--> RCA Agent
      +--> Recommendation Agent
      |
      v
Amazon Bedrock
      |
      v
S3 reports/*.json
      |
      v
CloudWatch Logs + Metrics
```

The deterministic engine establishes the evidence. Specialized agents interpret that evidence. Recommendations remain advisory and automatic destructive mutation is disabled.

## Current status

- Phase 0 — Repository foundation: complete
- Phase 1 — Data foundation: complete
- Phase 2 — Deterministic reliability engine: complete
- Phase 3 — Multi-agent reasoning + local E2E: complete
- Phase 4 — AWS runtime and E2E validation: complete
- Phase 5 — Agent evaluation and observability hardening: complete
- Phase 6.1 — Cost and latency evidence baseline: complete
- Phase 6.2 — Repeated performance benchmark: complete
- Phase 6.3 — Security and IAM review: complete
- Phase 6.4 — Failure/retry and operational resilience review: complete
- Phase 6.5 — Final portfolio walkthrough and architecture evidence: complete

## Portfolio evidence checkpoint

The platform has been validated through repeated local, CI, and live AWS checkpoints. The deployed `agentic-data-reliability` stack in `us-east-1` uses S3, EventBridge, Lambda, Amazon Bedrock, CloudWatch, and an SQS failure destination.

### Live AWS validation

A fresh intentionally faulty dataset traversed the production-style S3 → EventBridge → Lambda → Bedrock workflow and produced a persisted reliability report. CloudWatch recorded:

| Metric | Observed value |
|---|---:|
| `DatasetsProcessed` | `1` |
| `DatasetsFailed` | `1` |
| `ProcessingDurationMs` | `9281 ms` average |

The corresponding reliability report had status `failed`, score `35`, and five findings (four errors and one warning). The `failed` report status represents the dataset's reliability assessment; it is distinct from a platform/runtime failure.

### Repeated performance benchmark

Three fresh executions of the representative `mixed_issues.csv` dataset produced persisted reports and these observed duration metrics:

| Run | Processing duration |
|---|---:|
| `benchmark-run-1c` | 9055 ms |
| `benchmark-run-2` | 10779 ms |
| `benchmark-run-3` | 8067 ms |
| **Mean** | **9300 ms (9.3 s)** |

Observed latency ranged from **8.1 to 10.8 seconds**. This is a measured evidence baseline, not a production SLA. No fabricated dollar cost is claimed; meaningful cost analysis requires Bedrock token usage and account billing data.

## Security posture

The AWS boundary includes S3 AES-256 server-side encryption with Bucket Key, versioning, all four Public Access Block controls, and an explicit deny for non-TLS requests. Lambda S3 access is scoped to the project bucket, CloudWatch writes are restricted to the project namespace, and Bedrock access is limited to inference actions. The configurable Bedrock resource remains `*` as a documented portability trade-off.

## Resilience posture

Failures have explicit, bounded recovery paths:

- Transient Bedrock service failures use bounded exponential-backoff retries with jitter.
- Malformed or schema-invalid recommendation output gets one repair attempt.
- Lambda surfaces input-processing failures as invocation errors instead of silently acknowledging them.
- Lambda asynchronous retries are capped at two attempts within one hour.
- Exhausted failures are routed to an automatically provisioned SQS failure destination.
- Non-input objects are skipped without entering a retry loop.

Durable idempotency for multi-record/replayed events remains a documented future hardening item. Report keys are deterministic, preventing unbounded duplicate report objects.

## Repository layout

```text
.github/                 CI, templates, CODEOWNERS, Dependabot
data/sample/             deterministic sample dataset
data/evaluation/         representative reliability evaluation cases
docs/                    architecture, evaluation, execution, E2E, performance, security, resilience and project plan
infra/                   AWS SAM infrastructure
src/agents/              Bedrock adapter and specialized agents
src/reliability/         deterministic reliability engine
src/lambda_handler.py    S3-triggered Lambda entry point
tests/                   unit, contract and evaluation tests
```

## Local development

Python 3.12+ is the supported baseline.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest -q
```

The test suite uses fakes for AWS/Bedrock boundaries, so unit tests do not require AWS credentials.

## AWS deployment

AWS SAM is defined in `infra/template.yaml`.

```text
S3 input/*.csv
  -> EventBridge ObjectCreated
  -> Lambda
  -> deterministic reliability analysis
  -> Bedrock agents
  -> S3 reports/*.json
  -> CloudWatch logs/metrics
```

The stack is designed around least-privilege permissions and keeps automatic destructive remediation disabled.

## Documentation

See:
- [Architecture](docs/architecture.md)
- [AWS execution boundary](docs/aws-execution-boundary.md)
- [Agent evaluation](docs/agent-evaluation.md)
- [E2E validation](docs/e2e-validation.md)
- [Performance and cost evidence](docs/performance.md)
- [Security and IAM review](docs/security-iam-review.md)
- [Failure, retry, and resilience review](docs/resilience-review.md)
- [Project plan](docs/project-plan.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Engineering principles

- Evidence first
- Specialized agents
- Typed handoffs
- Least-privilege IAM
- Human-reviewed remediation
- AWS-independent tests
- Measured before optimized
- Small, explainable architecture

## License

MIT License — see [LICENSE](LICENSE).
