# Repository guidance

- Keep every example linked from `README.md` understandable on its own. Files explicitly marked
  as compatibility entry points may delegate to their canonical example.
- Keep examples grouped by provider or challenge type and run them with `python -m` from the
  repository root.
- Add a module description with `What it does` and `How it works` before implementation details.
- Use matching `STEP-*` comments for the important actions in the executable flow.
- Explain CAPTCHA-specific extraction, task creation, solution application, and acceptance checks.
- After changing Python, run `ruff check .` and `ruff format --check .`.
