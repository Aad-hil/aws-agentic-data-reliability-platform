# Tableau Reliability UI

## Purpose

Tableau is the read-only BI and presentation layer for the AWS Agentic Data Reliability Platform. Detection, evidence generation, root-cause analysis, and remediation recommendations remain in the AWS application layer.

## Data flow

```text
S3 reliability reports
        |
        v
Tableau-oriented CSV extracts
        |
        v
Amazon S3 / tableau/
        |
        v
Amazon Athena
        |
        v
Tableau Desktop
```

The current analytical database is `reliability_ui` in Athena.

## Athena analytical model

Three views are exposed for Tableau:

### `v_dataset_runs`

One row per reliability processing run.

Fields:

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

One row per reliability finding.

Fields:

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

One row per RCA hypothesis/agent insight. Recommendation fields are repeated at this grain so the Tableau layer can present the hypothesis and recommendation together.

Fields:

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

## Tableau relationships

The three logical datasets are related by `run_id`:

```text
v_dataset_runs.Run Id
       |
       +---- v_findings.Run Id
       |
       +---- v_agent_insights.Run Id
```

Findings and agent insights are not joined directly to each other. This avoids multiplying finding rows by RCA hypothesis rows when both are displayed for the same run.

## Current dashboards

### Data Reliability Overview

Provides the portfolio-facing summary:

- Dataset context
- Run status
- Quality score
- Finding count
- Severity breakdown
- Findings detail
- RCA and recommendations

Selecting a finding in the findings table filters the Incident Investigation dashboard to the corresponding `finding_id`.

### Incident Investigation

Provides the detailed investigation view:

- Run context
- Finding severity and check type
- Affected column
- Description
- Observed and expected values
- Affected row count
- RCA hypotheses
- Recommendation and recommendation risk

## Validation case

The current demonstration uses `production_orders_1000_faulty`:

- 1,005 rows
- Failed reliability status
- Quality score: 0
- 7 findings
- 1 critical finding
- 6 error findings
- 0 warnings
- 0 informational findings
- 3 RCA hypotheses

The seven findings represent issue-class events; the dataset contains five duplicate records as part of the injected uniqueness scenario. Finding counts must not be interpreted as seven distinct bad rows.

## Connection

Tableau Desktop connects to Amazon Athena in `us-east-1` using the Athena JDBC driver and the project's Athena query-results S3 location. Credentials are supplied locally and are never committed to the repository.

For the current setup, the Athena staging/query-results location is:

```text
s3://agentic-data-reliability-reliabilitybucket-dtgb89x1do3c/athena-results/
```

The Tableau layer is intentionally configured as a live Athena connection rather than copying reliability data into Tableau-managed storage.

## Evidence and security rules

- Never commit AWS access keys, secret keys, session tokens, or `.env` files.
- Do not include credentials in screenshots.
- Use synthetic/demo data for portfolio evidence.
- Do not move reliability detection or remediation decisions into Tableau.
- CloudWatch remains the operational observability layer.
- Tableau remains read-only with respect to reliability results.

## Known limitation

The current reliability report does not contain processing duration as a Tableau field. Processing duration is emitted through CloudWatch as `ProcessingDurationMs`. Tableau therefore does not fabricate or duplicate that metric. If a future analytical requirement needs duration trends, a deliberately versioned enrichment of the analytical contract can expose it.

## Scope

The Tableau phase intentionally avoids building a custom web application. The same Athena analytical contract can support a future application if a custom UI becomes necessary.
