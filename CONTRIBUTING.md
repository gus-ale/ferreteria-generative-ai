# Contributing

1. Create a branch from `main`.
2. Keep secrets outside the repository.
3. Add tests for behavior changes.
4. Add or update an eval for agent behavior changes.
5. Run:

```bash
ruff check .
ruff format --check .
pytest
python -m evals.run_evals
```

6. Explain security, quality, cost, and latency impact in the pull request.
