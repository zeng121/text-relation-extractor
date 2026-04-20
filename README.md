# Text Relation Extractor

Local-first full-stack app for turning free-form Chinese text into a relationship graph, timeline, and structured JSON output.

The backend is a FastAPI service that chooses an extractor strategy at runtime:
- Rule extraction when no LLM credentials are configured.
- LLM extraction when a supported provider key is present.
- Automatic fallback to rule extraction when the LLM path fails.

The frontend is a Vite app that submits text to the backend and renders the response as a graph, timeline, status panel, and raw JSON.

## Architecture

```text
text-relation-extractor/
├── backend/
│   ├── app/                 # FastAPI factory, routes, settings, logging, errors
│   ├── domain/              # Shared extraction models and contracts
│   ├── services/            # Rule extractor, LLM extractor, orchestrator, normalization
│   ├── tests/               # pytest unit and integration coverage
│   ├── main.py              # ASGI entrypoint
│   └── pyproject.toml       # Python dependencies and tool config
├── frontend/
│   ├── src/
│   │   ├── api/             # Backend request layer
│   │   ├── components/      # UI renderers and bindings
│   │   ├── graph/           # Cytoscape renderer
│   │   ├── state/           # Frontend state transitions
│   │   └── utils/           # Example data and helpers
│   ├── tests/               # Vitest coverage
│   ├── package.json         # Frontend scripts
│   └── vite.config.js       # Dev server and test config
├── .env.example             # Shell template for optional backend env vars
├── .editorconfig
├── CONTRIBUTING.md
└── .github/workflows/ci.yml
```

## Requirements

- Python 3.11+
- `uv`
- Node.js 18.18+
- npm

## Local Development

### 1. Backend

```bash
cd backend
uv sync --dev
uv run uvicorn main:app --reload
```

Backend URLs:
- API: `http://127.0.0.1:8000`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Frontend URL:
- App: `http://127.0.0.1:5173`

The frontend targets `http://127.0.0.1:8000` by default.

## Environment Variables

The backend reads environment variables directly from the shell. `.env.example` is a reference template only; it is not auto-loaded by the app.

Supported provider keys, checked in priority order:
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `GLM_API_KEY`
- `KIMI_API_KEY`
- `MINIMAX_API_KEY`
- `OPENCODE_ZEN_API_KEY`
- `OPENCODE_GO_API_KEY`
- `HF_TOKEN`

Optional provider-specific overrides are also supported through matching `*_BASE_URL` and `*_MODEL` variables in `.env.example`.

Example:

```bash
cp .env.example .env
set -a
source .env
set +a
```

If no supported API key is exported, the backend stays in rules-only mode.

## API Contract

### `GET /`

Health check response:

```json
{"message":"backend is running"}
```

### `POST /extract`

Request body:

```json
{"text":"张三上周加入电商项目，负责后端开发。"}
```

Response shape:

```json
{
  "nodes": [],
  "edges": [],
  "timeline": [],
  "extraction_mode": "rules",
  "warnings": []
}
```

`extraction_mode` indicates which extractor produced the result. `warnings` surfaces fallback and normalization issues without failing the request.

## Quality Gates

Backend:

```bash
cd backend
uv sync --dev
uv run ruff check .
uv run mypy .
uv run pytest -v
```

Frontend:

```bash
cd frontend
npm ci
npm run lint
npm run format:check
npm test -- --run
npm run build
```

## Repository Standards

- Keep repo-level docs and CI in sync with the current architecture.
- Prefer local development and verification before opening a pull request.
- Do not commit secrets, local virtualenvs, node modules, or generated build output.

See `CONTRIBUTING.md` for setup details and pull request expectations.

## License

MIT. See `LICENSE`.
