"""Configuration for deterministic reliability rules."""

# Existing customer rules are intentionally unchanged. New dataset profiles are
# additive so existing evaluations continue to use QUALITY_RULES by default.
QUALITY_RULES = (
    {"id": "required_columns", "type": "completeness", "columns": ("customer_id", "email", "age", "plan"), "severity": "error"},
    {"id": "customer_id_unique", "type": "uniqueness", "column": "customer_id", "severity": "critical"},
    {"id": "domain_validity", "type": "validity", "severity": "error"},
    {"id": "expected_schema", "type": "schema", "columns": ("customer_id", "email", "age", "plan"), "severity": "critical"},
)

ORDERS_QUALITY_RULES = (
    {"id": "required_columns", "type": "completeness", "columns": (
        "order_id", "customer_id", "order_date", "country", "plan", "product_category",
        "quantity", "unit_price", "discount_rate", "order_amount", "payment_method",
        "channel", "status",
    ), "severity": "error"},
    {"id": "order_id_unique", "type": "uniqueness", "column": "order_id", "severity": "critical"},
    {"id": "orders_domain_validity", "type": "orders_validity", "severity": "error"},
    {"id": "expected_orders_schema", "type": "schema", "columns": (
        "order_id", "customer_id", "order_date", "country", "plan", "product_category",
        "quantity", "unit_price", "discount_rate", "order_amount", "payment_method",
        "channel", "status",
    ), "severity": "critical"},
)
