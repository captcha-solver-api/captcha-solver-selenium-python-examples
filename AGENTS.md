# Repository guidance

- Keep every public file in `examples/` understandable on its own.
- Add a module description with `What it does` and `How it works` before implementation details.
- Use matching `STEP-*` comments for the important actions in the executable flow.
- Explain CAPTCHA-specific extraction, task creation, solution application, and acceptance checks.
- After changing Python, run `ruff check .` and `ruff format --check .`.
