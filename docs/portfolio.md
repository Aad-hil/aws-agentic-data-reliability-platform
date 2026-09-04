# Portfolio Guide

## One-line project description

An AWS-native multi-agent data reliability platform that detects data quality issues with deterministic evidence, uses specialized Bedrock agents for root-cause analysis and safe recommendations, and exposes the results through Athena and Tableau.

## Resume-ready version

**AWS Agentic Data Reliability Platform** — Python, AWS Lambda, Amazon S3, EventBridge, Amazon Bedrock, Athena, CloudWatch, SQS, Tableau

- Built an event-driven AWS data reliability pipeline that profiles incoming CSV data, applies deterministic quality rules, and produces evidence-backed reliability reports.
- Designed a specialized multi-agent workflow for detection, root-cause analysis, and remediation recommendations using Amazon Bedrock, with typed handoffs and destructive mutation disabled.
- Added an Athena analytical layer and read-only Tableau dashboards for dataset health, findings, incidents, RCA hypotheses, and recommendations without moving reliability decisions into the BI layer.
- Validated the deployed workflow with representative faulty datasets, regression tests, resilience controls, security/IAM review, and repeated performance measurements.

## Interview talking points

### Why deterministic checks plus agents?

Deterministic checks establish reproducible evidence. Agents interpret that evidence for RCA and recommendations, so model output does not become the source of truth for basic reliability measurements.

### Why Tableau instead of putting logic in the dashboard?

Tableau is intentionally a consumption layer. Reliability detection, evidence generation, RCA orchestration, and recommendation safety remain in the application/AWS workflow. Athena provides the normalized analytical contract between the pipeline and BI layer.

### How is the data model designed?

The analytical layer separates three grains:

- `v_dataset_runs` — one row per processing run
- `v_findings` — one row per reliability finding
- `v_agent_insights` — one row per RCA hypothesis

Relationships are anchored on `run_id`. Findings and agent hypotheses are not directly joined, preventing row multiplication in the dashboard.

### What was validated?

The representative `production_orders_1000_faulty` report contained 1005 rows, failed reliability status, score 0, 7 findings, 1 critical finding, 6 error findings, and 3 RCA hypotheses. Athena validation confirmed the expected analytical grains and shared incident context.

## Demo flow

1. Upload a CSV to the project S3 input location.
2. EventBridge triggers the Lambda workflow.
3. The deterministic reliability engine establishes findings and evidence.
4. Detection, RCA, and recommendation agents interpret the evidence.
5. The generated report is persisted to S3 and operational telemetry is emitted to CloudWatch.
6. The normalized analytical contract is exposed through Athena.
7. Tableau presents the run health, findings, and RCA/recommendation context.
8. Selecting a finding in the Overview opens the corresponding Incident Investigation context.

## Evidence to capture for a portfolio walkthrough

Keep the walkthrough focused on a small set of artifacts:

1. Architecture diagram showing the AWS event-driven pipeline and Tableau/Athena presentation layer.
2. AWS validation evidence showing a faulty dataset entering the workflow and a generated report.
3. Tableau Reliability Overview dashboard.
4. Tableau Incident Investigation dashboard after selecting a finding.
5. GitHub repository showing tests, infrastructure, agent code, analytical export, and documentation.

Avoid publishing screenshots containing AWS account identifiers, access keys, secret values, private endpoints, or other personal/account information.

## Scope boundary

This is a portfolio-scale reliability platform. Durable idempotency for replayed/multi-record events remains a documented production-hardening item. The project should be presented as a well-tested, AWS-native reference implementation rather than as a claim of production SLA or enterprise-scale load testing.
