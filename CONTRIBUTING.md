# Contributing

Thanks for contributing.

## Development workflow

1. Create a focused feature or fix branch from `main`.
2. Keep commits small and use clear, imperative commit messages.
3. Add or update tests for behavioral changes.
4. Update documentation when architecture or operational behavior changes.
5. Open a pull request using the repository template.
6. Ensure CI passes before merging.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

## Engineering expectations

- Keep agent responsibilities narrow and explicit.
- Preserve typed contracts between agents.
- Keep deterministic reliability checks independent from model inference.
- Do not commit credentials, tokens, `.env` files, or generated artifacts.
- Keep AWS permissions scoped to the resources and actions required.
- Prefer reversible, advisory remediation over automatic destructive mutation.

## Pull requests

A PR should explain the problem, the design, validation performed, and any AWS/IAM impact. Avoid mixing unrelated refactors with feature work.
