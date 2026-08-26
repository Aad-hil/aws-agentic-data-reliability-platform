# AWS Agent Execution — Phase 4.2

Phase 4.2 connects the S3-triggered Lambda to the existing Detection → RCA → Recommendation workflow.

Flow:
S3 input CSV → Lambda → deterministic profiling/evaluation → Detection → RCA → Recommendation → JSON report in S3.

Lambda constructs one BedrockClient and injects it into all three specialized agents. The orchestrator remains responsible for sequencing and state handoff.

Set BEDROCK_MODEL_ID to a model enabled in the deployment region. AWS credentials come from the Lambda execution role; no credentials are stored in source control.

The deterministic report remains the source of reliability evidence. Agent outputs continue through typed validation. Recommendations remain advisory and automatic mutation stays disabled.

The agents execute sequentially, making one Bedrock call per agent. This keeps the workflow easy to reason about and test.

## Phase 4 E2E validation

Validated in AWS `us-east-1` against the deployed `agentic-data-reliability` stack.

Controlled test input:
- `input/customers-e2e-003.csv`
- 50 rows
- 8 columns

Observed execution:
- S3 object upload triggered the EventBridge rule.
- Lambda invocation completed with `processed: 1` and `failures: 0`.
- Bedrock Nova 2 Lite invocation succeeded after the Lambda role was granted `bedrock:InvokeModel` permission for the inference profile.
- Robust JSON parsing handled the model response successfully.
- Detection, RCA, and Recommendation stages completed.
- Report persisted to `reports/customers-e2e-003.json` (12,692 bytes).

Report result:
- Reliability status: `failed` (dataset quality result, not Lambda execution failure)
- Reliability score: `35/100`
- Findings: 5 total — 4 errors and 1 warning
- RCA hypotheses and remediation recommendation were generated.
- `automatic_mutation_allowed` was `false`.

This validates the runtime path end-to-end while preserving the separation between deterministic data-quality evidence, model-based interpretation, and human-reviewed remediation.
