# Contributing

## Development Setup

### Backend

```bash
cd backend
uv sync --dev
uv run uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Environment

- Review `.env.example` for supported backend provider variables.
- Export the variables you need in your shell before starting the backend.
- Do not commit `.env`, secrets, API keys, or local credential files.

## Quality Gates

Run the same checks locally that CI runs.

### Backend

```bash
cd backend
uv sync --dev
uv run ruff check .
uv run mypy .
uv run pytest -v
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run format:check
npm test -- --run
npm run build
```

## Pull Requests

- Keep changes scoped to the task you are solving.
- Update docs and configuration when behavior or workflows change.
- Include test or verification evidence in the PR description.
- Call out known limitations, skipped checks, or follow-up work explicitly.
- Do not revert or overwrite unrelated changes in the branch.

## Style And Tooling

- Follow `.editorconfig`.
- Use the existing backend and frontend script/tooling instead of ad hoc alternatives.
- Prefer small, reviewable commits with clear messages.
