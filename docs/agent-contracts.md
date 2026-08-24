# Agent Contracts

## DetectionInput
- reliability_report
- dataset metadata

## DetectionOutput
- incident_id
- priority
- failed_checks
- severity
- evidence

## RCAInput
- incident
- profile metrics
- dataset metadata

## RCAOutput
- incident_id
- hypotheses
- evidence
- confidence
- uncertainty

## RecommendationInput
- incident
- RCA result

## RecommendationOutput
- incident_id
- recommendation
- rationale
- risk
- evidence

All contracts should be JSON-serializable and validated before handoff.
