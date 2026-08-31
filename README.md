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

### Live AWS validation checkpoint

The deployed `agentic-data-reliability` stack in `us-east-1` was validated with a fresh intentionally faulty dataset. The run successfully traversed S3 → EventBridge → Lambda → Bedrock workflow → reliability report → CloudWatch observability.

Observed CloudWatch datapoints from the fresh E2E run:

| Metric | Observed value |
|---|---:|
| `DatasetsProcessed` | `1` |
| `DatasetsFailed` | `1` |
| `ProcessingDurationMs` | `9281 ms` |

The reliability report for the test dataset was persisted to S3 with status `failed`, score `35`, and five findings (four errors and one warning). This validates both the data-quality path and the operational telemetry path.

## Performance and cost baseline

The fresh E2E execution completed in approximately **9.3 seconds** for a three-row dataset. This is a measured latency baseline, not a production SLA. The repository deliberately avoids claiming a fabricated single-run dollar cost; actual cost depends on Lambda duration/memory, Bedrock token usage, request volume, and account pricing.

The next useful benchmark is a repeated run across representative clean and faulty datasets, capturing latency and model usage before making optimization decisions.

See [Performance and cost evidence](docs/performance.md) for the measurement and interpretation.

## Repository layout

```text
.github/                 CI, templates, CODEOWNERS, Dependabot
data/sample/             deterministic sample dataset
data/evaluation/         representative reliability evaluation cases
docs/                    architecture, evaluation, execution, E2E, performance and project plan
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

Tests use fakes for AWS/Bedrock boundaries, so the unit suite does not require AWS credentials.

## AWS deployment

AWS SAM is defined in `infra/template.yaml`. The deployed target is:

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

See:
- [Architecture](docs/architecture.md)
- [AWS execution boundary](docs/aws-execution-boundary.md)
- [Agent evaluation](docs/agent-evaluation.md)
- [E2E validation](docs/e2e-validation.md)
- [Performance and cost evidence](docs/performance.md)
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
