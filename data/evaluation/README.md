# Evaluation Datasets

Small controlled datasets used to evaluate deterministic data-quality checks and downstream agent behavior.

| Dataset | Scenario | Expected outcome |
|---|---|---|
| `clean.csv` | No intentional defects | Pass / high reliability score |
| `missing_values.csv` | Missing required `age` | Fail with completeness finding |
| `invalid_values.csv` | Invalid email, age, and plan | Fail with validity findings |
| `schema_drift.csv` | Unexpected `loyalty_tier` column | Fail with schema finding |
| `mixed_issues.csv` | Missing, invalid, and domain errors | Fail with multiple findings |

These fixtures are intentionally small and deterministic so automated tests can assert known quality outcomes without relying on LLM-generated judgments.

The evaluation layer separates deterministic data-quality facts from the agentic stages that interpret findings, generate RCA hypotheses, and recommend remediation.
