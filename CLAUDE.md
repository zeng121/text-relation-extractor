# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Text Relation Extractor is a local-first full-stack app for turning free-form Chinese text into a relationship graph, timeline, and structured JSON.

- Backend: FastAPI service in `backend/` with runtime extraction strategy selection.
- Frontend: Vite app in `frontend/` that posts text to the backend and renders graph, timeline, status/warnings, and raw JSON.
- The frontend assumes the backend is available at `http://127.0.0.1:8000`; Vite runs at `http://127.0.0.1:5173`.

## Common commands

### Backend

```bash
cd backend
uv sync --dev
uv run uvicorn main:app --reload
```

Backend quality gates, matching CI:

```bash
cd backend
uv run ruff check .
uv run mypy .
uv run pytest -v
```

Run a single backend test file or test:

```bash
cd backend
uv run pytest tests/unit/test_rule_extractor.py -v
uv run pytest tests/integration/test_extract_api.py::test_extract_falls_back_to_rules_with_warning_when_llm_fails -v
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Frontend quality gates, matching CI:

```bash
cd frontend
npm run lint
npm run format:check
npm test -- --run
npm run build
```

Run a single frontend test file or test name:

```bash
cd frontend
npm test -- tests/ui-flow.test.js --run
npm test -- tests/ui-flow.test.js --run -t "renders warnings as text instead of HTML"
```

## Backend architecture

`backend/main.py` exposes the ASGI app from `app.factory.create_app()`. The factory configures logging, permissive CORS, app settings, routers, and exception handlers.

The HTTP surface is intentionally small:

- `GET /` returns a health response.
- `POST /extract` validates `{"text": "..."}` with Pydantic and returns `nodes`, `edges`, `timeline`, `extraction_mode`, and `warnings`.

Extraction flow:

1. `app.routes.extract()` builds an `ExtractionOrchestrator` per request with the current `Settings`, `OpenAICompatibleLLMExtractor`, and `RegexRuleExtractor`.
2. `Settings` loads repository-root `.env` values once at import time without overriding shell environment variables, then enables LLM mode when any supported provider key is present.
3. `ExtractionOrchestrator` uses rules when LLM mode is disabled; otherwise it tries the LLM extractor and falls back to rules with a warning on any LLM failure.
4. `OpenAICompatibleLLMExtractor` sends an OpenAI-compatible chat completions request, extracts a JSON object from the response, and passes it to `normalize_llm_payload()`.
5. `normalize_llm_payload()` deduplicates nodes/edges, maps unknown node types to `other`, auto-creates missing edge endpoint nodes, filters timeline related nodes to known IDs, and records normalization warnings.
6. `RegexRuleExtractor` is the no-credential fallback for Chinese text; it extracts simple people, organizations, projects, roles, relationships, and timeline events with regexes.

Core backend data structures live in `domain.models` as frozen dataclasses. API schemas in `backend/schemas.py` convert those dataclasses to Pydantic response models.

Supported node types are shared conceptually across backend normalization and frontend graph styling: `person`, `organization`, `project`, `role`, `document`, `artifact`, `resource`, `spec`, `hardware`, `deliverable`, and `other`.

## Frontend architecture

`frontend/src/main.js` wires the UI together through `createApp()`. It queries fixed DOM IDs from `index.html`, pre-fills the default Chinese example, renders default graph data, then posts user input when the generate button is clicked.

Frontend data flow:

1. `api/extract.js` posts `{ text }` to `/extract`, converts HTTP/network failures into user-facing Chinese messages, and normalizes missing arrays or warnings.
2. `state/app-state.js` is the small state reducer for idle/loading/success/error plus extraction mode and warnings.
3. `graph/render-graph.js` converts API graph data with `utils/to-elements.js`, recreates a Cytoscape instance on each render, styles nodes by type, and renders node details on tap.
4. Component renderers under `src/components/` update status, warnings/mode, timeline, detail card, and raw JSON.
5. Tests use dependency injection (`fetchImpl`, `graphRenderer`, and jsdom DOM setup) instead of requiring a live backend or real Cytoscape rendering for UI-flow coverage.

## Environment and provider behavior

The backend reads optional provider credentials from the repository-root `.env` or existing shell environment. Supported keys are checked in priority order in `app.settings.LLM_API_KEY_ENV_VARS`, and provider-specific `*_BASE_URL` / `*_MODEL` overrides are handled in `services.llm_extractor`.

If no supported key is configured, the app remains in rules-only mode. If an LLM provider is configured but the request fails or returns invalid output, the API still returns a rules result and includes a warning.

## Testing notes

Backend integration tests use `httpx.ASGITransport` against `create_app(settings=Settings(llm_enabled=False/True))`, so most API behavior can be tested without starting uvicorn. Monkeypatch `OpenAICompatibleLLMExtractor.extract` or `ExtractionOrchestrator.extract` for fallback and error-path tests.

Frontend tests run with Vitest. `vite.config.js` sets the default test environment to `node`, and tests that need DOM APIs opt into jsdom with `/** @vitest-environment jsdom */`.
