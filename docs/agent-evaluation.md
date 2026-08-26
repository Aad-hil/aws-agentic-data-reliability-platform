# Agent Evaluation

## Purpose

Phase 5.4 evaluates the live agentic workflow without making Bedrock calls part of normal CI.

The evaluation consumes a generated reliability report and scores four deterministic contract checks:

1. Detection failed checks are supported by deterministic findings.
2. Detection affected columns are supported by deterministic findings.
3. RCA hypotheses contain evidence and bounded confidence values from 0 to 1.
4. Recommendations are actionable, evidence-backed, and keep automatic mutation disabled.

## Running locally

After obtaining a generated reliability report:

```bash
python3 scripts/evaluate_agent.py /path/to/report.json
```

Optionally save the result:

```bash
python3 scripts/evaluate_agent.py /path/to/report.json \
  --output /tmp/agent-evaluation.json
```

## Why this is separate from CI

The production workflow calls Amazon Bedrock, so a live model evaluation would introduce cost, latency, credentials, and model-variance into every pull request. CI therefore validates deterministic agent contracts, while this command provides an explicit live-evaluation checkpoint when a real Bedrock-generated report is available.

A future evaluation phase can add a curated set of expected model-quality judgments, but the first live gate deliberately focuses on safety and grounding rather than brittle exact-string matching.
