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
Tableau-oriented analytical extracts
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
| Amazon S3 | Store input datasets, reliability reports, and Tableau-oriented extracts |
| EventBridge | Trigger processing when input objects are created |
| AWS Lambda | Execute the reliability workflow |
| Reliability engine | Perform deterministic data-quality checks |
| Agentic workflow | Produce RCA hypotheses and recommendations |
| Amazon Bedrock | Support agentic reasoning where configured |
| Amazon Athena | Query the Tableau-oriented analytical data in S3 |
| Tableau | Visualize reliability metrics, findings, RCA, and recommendations |
| CloudWatch | Operational observability and AWS runtime monitoring |

## Tableau analytical model

The current UI exposes three logical datasets/views:

### `v_dataset_runs`

One record per reliability processing run.

Core fields:

- `run_id`
- `request_id`
- `dataset`
- `source`
- `processed_at`
- `row_count`
- `status`
- `quality_score`
- `finding_count`
- `info_count`
- `warning_count`
- `error_count`
- `critical_count`

### `v_findings`

One record per detected reliability finding.

Core fields:

- `run_id`
- `dataset`
- `finding_id`
- `check_type`
- `severity`
- `column_name`
- `description`
- `observed_value`
- `expected_value`
- `affected_row_count`
- `affected_rows`
- `evidence`

### `v_agent_insights`

One record per RCA hypothesis/agent insight.

Core fields:

- `run_id`
- `dataset`
- `incident_id`
- `priority`
- `issue_severity`
- `affected_columns`
- `hypothesis`
- `confidence`
- `uncertainty`
- `hypothesis_evidence`
- `recommendation`
- `recommendation_rationale`
- `recommendation_risk`
- `recommendation_evidence`
- `automatic_mutation_allowed`

Processing duration is intentionally not duplicated into the Tableau contract because the current reliability report does not provide it as a report field. `ProcessingDurationMs` remains a CloudWatch operational metric.

## Tableau relationships

The three logical datasets are related by `run_id`:

```text
v_dataset_runs.Run Id
       |
       +---- v_findings.Run Id
       |
       +---- v_agent_insights.Run Id
```

Findings and agent insights are not joined directly. This preserves their one-to-many relationships to a run and avoids multiplying findings by RCA hypotheses.

## Dashboard views

The implemented portfolio UI contains:

1. **Data Reliability Overview** — dataset/run context, quality score, finding count, severity breakdown, findings detail, and RCA/recommendations.
2. **Incident Investigation** — detailed findings, evidence-oriented fields, affected-row information, and RCA/recommendations.

The Overview findings table has a Tableau filter action keyed by deterministic `finding_id`, allowing a selected finding to filter the Incident Investigation view.

## Design principles

- Keep the existing reliability engine unchanged.
- Keep Tableau read-only with respect to reliability results.
- Keep deterministic detection separate from agentic RCA/recommendation.
- Use synthetic/demo data only for portfolio evidence.
- Do not expose credentials, secrets, account identifiers, or PII in dashboard screenshots.
- Keep CloudWatch as the operational observability layer; Tableau is the analytical/presentation layer.
- Avoid unnecessary custom UI infrastructure when Tableau sufficiently demonstrates the presentation layer.

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
UI-5  Build Incident Investigation / Findings
  |
UI-6  Integrate RCA & Recommendations
  |
UI-7  Polish, validate, document, and capture portfolio evidence
```

## Initial scope decision

A custom web application is intentionally out of scope for this phase. Tableau is used to demonstrate the BI/presentation layer without adding unnecessary UI infrastructure. A future web application could consume the same analytical contract if the project later requires a custom product interface.
