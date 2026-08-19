# Architecture

## Goal

Build a small AWS-native multi-agent system that can identify data reliability problems, investigate likely causes, and produce an explainable result.

## Core Design

```text
                 +----------------+
                 |   Data Source  |
                 +-------+--------+
                         |
                         v
                 +---------------+
                 | Ingestion /   |
                 | Event Layer   |
                 +-------+-------+
                         |
                         v
              +-----------------------+
              | Reliability Detection |
              |        Agent           |
              +-----------+-----------+
                          |
             +------------+------------+
             |                         |
             v                         v
     +---------------+         +---------------+
     | Data Profiling|         | Quality Rules |
     +-------+-------+         +-------+-------+
             |                         |
             +------------+------------+
                          v
              +-----------------------+
              | Root Cause Analysis   |
              |        Agent           |
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | Recommendation /      |
              | Explanation Agent     |
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | Result + Audit Trail  |
              +-----------------------+
```

## Agent Responsibilities

### Reliability Detection Agent

Identifies anomalies or failed reliability checks and turns raw signals into a structured incident.

### Root Cause Analysis Agent

Uses available quality signals, metadata, and evidence to rank likely causes. It should explain why a cause was selected rather than returning an unsupported guess.

### Recommendation / Explanation Agent

Converts the investigation into a concise, human-readable finding with recommended next actions and confidence/evidence context.

## AWS Direction

AWS services will be introduced only when they provide a clear architectural benefit. Candidate areas include managed eventing, serverless compute, object storage, managed model inference, workflow/orchestration, logging, and monitoring.

The final service map will be documented after the first end-to-end slice is implemented.

## Design Principles

- Small, specialized agents
- Structured inputs and outputs
- Explicit evidence between agent steps
- Least-privilege AWS access
- Observable execution
- Deterministic checks around probabilistic agent behavior
- Testable business logic independent of AWS infrastructure where practical
