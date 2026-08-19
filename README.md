# AWS Agentic Data Reliability Platform

An AWS-native, multi-agent platform for detecting, diagnosing, and explaining data reliability issues with minimal human intervention.

## Project Status

🚧 **Phase 0 — Repository foundation**

This portfolio project is being built incrementally around four capabilities:

- Detect data quality and reliability issues
- Diagnose likely root causes
- Explain findings in human-readable language
- Recommend safe next actions

The implementation intentionally uses a small number of focused agents and managed AWS services instead of over-engineering the platform.

## Planned Flow

```text
Data Source
    |
    v
Ingestion / Event Layer
    |
    v
Reliability Detection Agent
    |
    +------> Profiling / Quality Checks
    |
    v
Root Cause Analysis Agent
    |
    v
Recommendation / Explanation Agent
    |
    v
Results + Audit Trail
```

The exact AWS service mapping will be added as the implementation evolves. The goal is to demonstrate practical AWS architecture, agentic orchestration, observability, and testable software design.

## Repository Structure

```text
aws-agentic-data-reliability-platform/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── docs/
│   ├── architecture.md
│   └── project-plan.md
├── src/
│   └── ...
└── tests/
```

## Local Setup

Python 3.11+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Copy `.env.example` to `.env` and configure only the variables required by the current phase.

## Development Principles

1. Keep the system portfolio-sized and demonstrable.
2. Prefer managed AWS services where they reduce operational overhead.
3. Keep each agent responsible for one clear capability.
4. Add tests with each meaningful implementation step.
5. Never commit credentials, secrets, or local environment files.
6. Favor explainability and traceability over unnecessary agent autonomy.

## Roadmap

See [`docs/project-plan.md`](docs/project-plan.md) for the implementation sequence.

## License

MIT License. See [`LICENSE`](LICENSE).
