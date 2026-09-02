# Tableau Reliability UI Architecture

## Purpose

The Tableau layer is a presentation and analytical layer for the AWS Agentic Data Reliability Platform. It visualizes reliability results produced by the existing AWS pipeline; it does not perform data-quality detection, root-cause analysis, remediation, or mutation.

## Architecture

```text
Input dataset
    |
    v
Amazon S3
    |
    v
EventBridge
    |
    v
AWS Lambda
    |
    +--> Deterministic reliability checks
    +--> Detection / RCA / recommendation workflow
    +--> Amazon Bedrock
    |
    v
Reliability reports in Amazon S3
    |
    v
BI-friendly analytical data
    |
    v
Amazon Athena
    |
    v
Tableau Reliability Dashboard
```

## Responsibilities

| Layer | Responsibility |
|---|---|
| Amazon S3 | Store input datasets and reliability reports |
| EventBridge | Trigger processing when input objects are created |
| AWS Lambda | Execute the reliability workflow |
| Reliability engine | Perform deterministic data-quality checks |
| Agentic workflow | Produce RCA hypotheses and recommendations |
| Amazon Bedrock | Support agentic reasoning where configured |
| Amazon Athena | Query the Tableau-oriented analytical data in S3 |
| Tableau | Visualize reliability metrics, findings, RCA, and recommendations |
| CloudWatch | Operational observability and AWS runtime monitoring |

## Tableau analytical model

The first UI implementation will expose three logical datasets:

### `dataset_runs`

One record per reliability processing run.

Core fields:

- `run_id`
- `dataset`
- `processed_at`
- `row_count`
- `status`
- `quality_score`
- `finding_count`
- `critical_count`
- `error_count`
- `warning_count`
- `duration_ms`

### `findings`

One record per detected reliability finding.

Core fields:

- `run_id`
- `dataset`
- `finding_id`
- `rule_id`
- `severity`
- `message`
- `affected_rows`
- `evidence`

### `agent_insights`

One record per RCA/recommendation insight.

Core fields:

- `run_id`
- `dataset`
- `issue_type`
- `hypothesis`
- `confidence`
- `recommendation`

## Dashboard views

The portfolio dashboard will be developed incrementally:

1. **Overview** — quality score, processed datasets, failed runs, critical findings, trends, and recent runs.
2. **Dataset Health** — selected dataset/run details and rule-level findings.
3. **Findings** — severity, rule, affected rows, and evidence.
4. **RCA & Recommendations** — agent-generated hypotheses, confidence, and recommendations.

## Design principles

- Keep the existing reliability engine unchanged.
- Keep Tableau read-only with respect to reliability results.
- Keep deterministic detection separate from agentic RCA/recommendation.
- Use synthetic/demo data only for the portfolio dashboard.
- Do not expose credentials, secrets, account identifiers, or PII in dashboard screenshots.
- Keep CloudWatch as the operational observability layer; Tableau is the analytical/presentation layer.

## Implementation sequence

```text
UI-0  Architecture and data contract
  |
UI-1  Prepare Tableau-ready data
  |
UI-2  Create Athena analytical layer
  |
UI-3  Connect Tableau to Athena
  |
UI-4  Build Overview dashboard
  |
UI-5  Build Dataset Health and Findings
  |
UI-6  Build RCA & Recommendations
  |
UI-7  Polish, validate, document, and capture portfolio evidence
```

## Initial scope decision

A custom web application is intentionally out of scope for this phase. Tableau is used to demonstrate the BI/presentation layer without adding unnecessary UI infrastructure. A future web application could consume the same analytical contract if the project later requires a custom product interface.
