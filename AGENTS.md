# Repository guidance

- Keep every file in `examples/` understandable and runnable on its own; do not hide the main
  flow in local helper modules or compatibility entry points.
- Keep examples grouped by provider or challenge type and directly runnable from the repository
  root with `python examples/<group>/<example>.py`.
- Add a module description with `What it does` and `How it works` before implementation details.
- Use matching `STEP-*` comments for the important actions in the executable flow.
- Explain CAPTCHA-specific extraction, task creation, solution application, and acceptance checks.
- After changing Python, run `ruff check .` and `ruff format --check .`.
