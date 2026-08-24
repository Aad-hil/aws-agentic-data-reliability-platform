"""Configuration for the deterministic reliability rules."""

QUALITY_RULES = (
    {"id": "required_columns", "type": "completeness", "columns": ("customer_id", "email", "age", "plan"), "severity": "error"},
    {"id": "customer_id_unique", "type": "uniqueness", "column": "customer_id", "severity": "critical"},
    {"id": "domain_validity", "type": "validity", "severity": "error"},
    {"id": "expected_schema", "type": "schema", "columns": ("customer_id", "email", "age", "plan"), "severity": "critical"},
)
