# Architecture

## Goal

Detect data reliability failures deterministically, then use specialized Bedrock-powered agents to investigate the evidence and recommend safe next actions.

## Runtime

```text
S3 input/*.csv
      |
ObjectCreated
      v
Lambda
      |
      +--> Profiler
      +--> Rules / Evaluator
      |
      v
Reliability Report
      |
      v
Orchestrator
      |
      +--> Detection -> Incident
      +--> RCA -> Root-cause hypotheses
      +--> Recommendation -> Advisory action
      |
      v
Amazon Bedrock
      |
      v
S3 reports/*.json
      |
      +--> CloudWatch Logs + Metrics
      +--> SQS failure destination (exhausted async failures)
```

## Responsibilities

| Component | Responsibility |
| --- | --- |
| Profiler | Dataset statistics and metadata |
| Rules/Evaluator | Deterministic reliability findings |
| Detection Agent | Prioritize an incident from evidence |
| RCA Agent | Rank likely causes with evidence and uncertainty |
| Recommendation Agent | Produce reviewable remediation advice |
| Orchestrator | Sequence agents and preserve typed state |
| Lambda | AWS event-driven execution boundary |
| S3 | Input and report storage |
| EventBridge | Route S3 ObjectCreated events to Lambda |
| Bedrock | Model inference |
| CloudWatch | Logs and operational metrics |
| SQS failure destination | Capture exhausted asynchronous Lambda failures |

## Design decisions

**Evidence-first AI:** agents receive structured reliability evidence rather than deciding whether a failure exists.

**Typed handoffs:** agent boundaries use explicit contracts.

**Advisory remediation:** automatic destructive mutation remains disabled.

**Layered AWS integration:** Lambda owns execution, the orchestrator owns sequencing, and the Bedrock adapter owns model invocation.

**Bounded recovery:** transient model failures retry locally, malformed model output gets one repair attempt, and asynchronous Lambda retries are capped with an SQS failure destination.

**Deterministic report identity:** reports use a stable dataset-based key to avoid unbounded duplicate report objects during replay.

## Security and reliability

- S3 server-side encryption and public-access controls are enabled.
- IAM is scoped to required services/actions, with the configurable Bedrock resource scope documented as the remaining limitation.
- Credentials are never committed.
- CI runs on pull requests and pushes to `main`.
- Tests run without live AWS access.
- Lambda failures are surfaced instead of silently acknowledged.
- Automatic destructive remediation remains disabled.
