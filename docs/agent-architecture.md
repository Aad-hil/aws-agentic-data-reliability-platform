# Agent Architecture

## 3.1 Goal

Define the smallest useful multi-agent workflow that reasons over the deterministic reliability evidence produced by Phase 2.

## Agent Roles

### 1. Reliability Detection Agent

**Purpose:** Interpret a reliability report and identify the highest-priority data-quality incident.

**Input:** Reliability report JSON.

**Output:** Structured incident containing:
- incident ID
- failed checks
- severity
- affected columns
- evidence
- priority

**Boundary:** It does not invent quality failures. The Phase 2 reliability engine remains the source of truth.

### 2. Root Cause Analysis Agent

**Purpose:** Investigate likely causes of the selected incident.

**Input:** Structured incident + profile metrics + relevant dataset metadata.

**Output:** Ranked root-cause hypotheses with supporting evidence and confidence.

**Boundary:** Every hypothesis must reference available evidence; uncertainty must be explicit.

### 3. Recommendation Agent

**Purpose:** Convert the RCA into an actionable remediation recommendation.

**Input:** Incident + RCA findings.

**Output:** Recommended action, expected impact, risk/limitations, and evidence summary.

**Boundary:** Recommendations are advisory. No destructive data mutation is performed by the first version.

## Orchestration

The first workflow is intentionally sequential:

```text
Reliability Report
       |
       v
Detection Agent
       |
       v
RCA Agent
       |
       v
Recommendation Agent
       |
       v
Final Incident Report
```

The orchestrator owns routing and state. Agents own specialized reasoning.

## Evidence Contract

Each handoff carries structured evidence:

```text
ReliabilityReport
    -> Incident
    -> RCAResult
    -> Recommendation
```

Free-form model text is not the system-of-record. Structured outputs are.

## AWS Direction

For the first AWS slice:
- Amazon Bedrock: managed model inference
- AWS Lambda: stateless agent execution where appropriate
- Amazon S3: datasets/reports
- Amazon CloudWatch: execution logs

We will not introduce additional AWS services until an end-to-end requirement justifies them.

## Safety and Reliability

- Deterministic checks precede agent reasoning.
- Agents cannot override quality evidence.
- Model failures must produce an explicit fallback/error state.
- No automatic data mutation in the initial release.
- Agent inputs/outputs should be auditable.
