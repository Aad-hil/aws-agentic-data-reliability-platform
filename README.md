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
      +--> CloudWatch Logs + Metrics
      +--> SQS failure destination
      |
      v
Tableau presentation layer
      ^
      |
Amazon Athena / reliability_ui
```

The deterministic engine establishes the evidence. Specialized agents interpret that evidence. Recommendations remain advisory and automatic destructive mutation is disabled. Tableau is a read-only analytical/presentation layer; it does not perform reliability detection or remediation decisions.

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
- Tableau UI — Athena analytical layer + portfolio dashboards: implemented on `feature/tableau-reliability-ui`

### Live AWS validation checkpoint

The deployed `agentic-data-reliability` stack in `us-east-1` was exercised repeatedly with the representative three-row `mixed_issues.csv` evaluation case. The workflow traverses S3 → EventBridge → Lambda → deterministic analysis → multi-agent Bedrock workflow → S3 report → CloudWatch observability.

Three benchmark executions produced persisted reports and these duration observations:

| Run | ProcessingDurationMs |
|---|---:|
| `benchmark-run-1c` | `9055 ms` |
| `benchmark-run-2` | `10779 ms` |
| `benchmark-run-3` | `8067 ms` |
| **Mean** | **9300 ms** |

This is a portfolio performance baseline, not a production SLA or load-test result.

## Security posture

- S3 AES-256 server-side encryption with Bucket Key
- S3 versioning for recovery
- All four S3 Public Access Block controls enabled
- Explicit S3 deny for non-TLS requests
- Lambda S3 permissions scoped to the project bucket
- CloudWatch metric writes limited to `PutMetricData` in the project namespace
- Bedrock limited to inference actions (`InvokeModel` and `Converse`)
- No credentials or `.env` files committed
- Destructive remediation remains disabled

The Bedrock resource is currently `*` as a documented portability trade-off for configurable inference profiles/models; the action set remains restricted.

## Resilience posture

- Bedrock retries transient throttling/service failures with bounded exponential backoff and jitter.
- Recommendation output gets one repair attempt when model output is malformed or schema-invalid.
- Lambda raises an invocation-level error when an input record fails.
- Lambda asynchronous retries are capped at 2 attempts within 1 hour.
- Exhausted failures are routed to an SQS failure destination for investigation/reprocessing.
- Invalid non-input objects are skipped without entering a retry loop.

The remaining production hardening item is durable idempotency for multi-record/replayed events.

## Repository layout

```text
.github/                 CI, templates, CODEOWNERS, Dependabot
data/sample/             deterministic sample dataset
data/evaluation/         representative reliability evaluation cases
docs/                    architecture, evaluation, execution, E2E, performance, security, resilience, UI and project plan
infra/                   AWS SAM infrastructure
scripts/                 data/portfolio utilities, including Tableau extract generation
src/agents/              Bedrock adapter and specialized agents
src/reliability/         deterministic reliability engine
src/lambda_handler.py    S3-triggered Lambda entry point
tests/                   unit, contract, evaluation and Tableau export tests
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

The local test suite is AWS-independent and uses fakes for AWS/Bedrock boundaries.

## AWS deployment

AWS SAM is defined in `infra/template.yaml`.

```bash
sam validate --template-file infra/template.yaml --lint
sam build --template-file infra/template.yaml
sam deploy
```

The stack provisions the S3/EventBridge/Lambda execution boundary, Bedrock integration, CloudWatch observability, dashboard, and Lambda failure destination.

## Tableau / BI layer

The Tableau layer consumes a normalized analytical contract through Amazon Athena. It is intentionally minimal: the goal is to demonstrate an AWS-to-BI product surface without moving reliability logic into the dashboard.

Current Tableau views:

- **Data Reliability Overview** — run context, quality score, finding count, severity breakdown, findings, and RCA/recommendations.
- **Incident Investigation** — detailed findings and RCA/recommendations.

The Overview findings table uses deterministic `finding_id` selection to filter Incident Investigation. The analytical model uses `run_id` relationships rather than directly joining findings to agent hypotheses, avoiding row multiplication.

See [Tableau Reliability UI](docs/tableau.md) and [Tableau UI Architecture](docs/ui-architecture.md) for the data contract, Athena model, connection setup, dashboard behavior, security rules, and known limitations.

## Documentation

- [Architecture](docs/architecture.md)
- [AWS execution boundary](docs/aws-execution-boundary.md)
- [Agent evaluation](docs/agent-evaluation.md)
- [E2E validation](docs/e2e-validation.md)
- [Performance and cost evidence](docs/performance.md)
- [Security and IAM review](docs/security-iam-review.md)
- [Failure, retry, and resilience review](docs/resilience-review.md)
- [Tableau Reliability UI](docs/tableau.md)
- [Tableau UI Architecture](docs/ui-architecture.md)
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
- BI/presentation logic separated from reliability decisions

## License

MIT License — see [LICENSE](LICENSE).
