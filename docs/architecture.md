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
S3 reports/*.json
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
| Bedrock | Model inference |

## Design decisions

**Evidence-first AI:** agents receive structured reliability evidence rather than deciding whether a failure exists.

**Typed handoffs:** agent boundaries use explicit contracts.

**Advisory remediation:** automatic destructive mutation remains disabled.

**Layered AWS integration:** Lambda owns execution, the orchestrator owns sequencing, and the Bedrock adapter owns model invocation.

## Security and reliability

- S3 server-side encryption is enabled.
- IAM is scoped to required services/actions.
- Credentials are never committed.
- CI runs on pull requests and pushes to `main`.
- Tests run without live AWS access.

Phase 4.3 will add explicit failure boundaries, retry policy, and structured operational logging.
