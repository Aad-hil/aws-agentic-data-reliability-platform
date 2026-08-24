# AWS Agent Execution — Phase 4.2

Phase 4.2 connects the S3-triggered Lambda to the existing Detection → RCA → Recommendation workflow.

Flow:
S3 input CSV → Lambda → deterministic profiling/evaluation → Detection → RCA → Recommendation → JSON report in S3.

Lambda constructs one BedrockClient and injects it into all three specialized agents. The orchestrator remains responsible for sequencing and state handoff.

Set BEDROCK_MODEL_ID to a model enabled in the deployment region. AWS credentials come from the Lambda execution role; no credentials are stored in source control.

The deterministic report remains the source of reliability evidence. Agent outputs continue through typed validation. Recommendations remain advisory and automatic mutation stays disabled.

The agents execute sequentially, making one Bedrock call per agent. This keeps the workflow easy to reason about and test.
