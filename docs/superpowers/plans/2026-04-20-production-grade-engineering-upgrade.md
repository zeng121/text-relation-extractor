# Production-Grade Engineering Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the current toy MVP into an engineering-grade open-source project for local development, covering both backend and frontend without expanding product scope.

**Architecture:** The backend will move to an app/domain/services layout with explicit extractor orchestration, centralized settings, and testable error handling. The frontend will move to a lightweight module-based build with isolated UI responsibilities, visible extraction warnings, and automated tests, while preserving the existing product surface.

**Tech Stack:** FastAPI, Pydantic, httpx, pytest, Ruff, mypy, Vite, Vitest, Testing Library, ESLint, Prettier, Cytoscape.js, GitHub Actions

---

## Planned File Structure

### Backend

- Modify: `backend/main.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/factory.py`
- Create: `backend/app/routes.py`
- Create: `backend/app/settings.py`
- Create: `backend/app/logging.py`
- Create: `backend/app/errors.py`
- Create: `backend/domain/__init__.py`
- Create: `backend/domain/models.py`
- Create: `backend/domain/contracts.py`
- Create: `backend/services/__init__.py`
- Create: `backend/services/orchestrator.py`
- Create: `backend/services/rule_extractor.py`
- Create: `backend/services/llm_extractor.py`
- Create: `backend/services/normalizer.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/unit/test_settings.py`
- Create: `backend/tests/unit/test_rule_extractor.py`
- Create: `backend/tests/unit/test_normalizer.py`
- Create: `backend/tests/integration/test_health.py`
- Create: `backend/tests/integration/test_extract_api.py`
- Modify: `backend/pyproject.toml`

### Frontend

- Modify: `frontend/index.html`
- Create: `frontend/package.json`
- Create: `frontend/package-lock.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/eslint.config.js`
- Create: `frontend/.prettierrc.json`
- Create: `frontend/src/main.js`
- Create: `frontend/src/api/extract.js`
- Create: `frontend/src/state/app-state.js`
- Create: `frontend/src/graph/render-graph.js`
- Create: `frontend/src/components/render-detail.js`
- Create: `frontend/src/components/render-status.js`
- Create: `frontend/src/components/render-timeline.js`
- Create: `frontend/src/components/render-json.js`
- Create: `frontend/src/components/bind-examples.js`
- Create: `frontend/src/utils/to-elements.js`
- Create: `frontend/src/utils/examples.js`
- Create: `frontend/tests/to-elements.test.js`
- Create: `frontend/tests/app-state.test.js`
- Create: `frontend/tests/ui-flow.test.js`
- Modify or replace: `frontend/style.css`

### Repo Quality And Docs

- Modify: `README.md`
- Create: `.editorconfig`
- Create: `.env.example`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `.github/workflows/ci.yml`
- Modify: `.gitignore`

## Task 1: Establish Backend App Skeleton And Quality Tooling

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/factory.py`
- Create: `backend/app/routes.py`
- Create: `backend/app/settings.py`
- Create: `backend/app/logging.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/unit/test_settings.py`
- Create: `backend/tests/integration/test_health.py`
- Modify: `backend/main.py`
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: Write the failing backend settings test**

```python
from app.settings import Settings


def test_settings_default_to_rules_when_no_api_keys(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings()
    assert settings.llm_enabled is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/test_settings.py -v`
Expected: FAIL with import or attribute errors because the settings module does not exist yet.

- [ ] **Step 3: Write the failing health integration test**

```python
from fastapi.testclient import TestClient

from app.factory import create_app


def test_health_check_returns_backend_status():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "backend is running"}
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/integration/test_health.py -v`
Expected: FAIL because the app factory does not exist yet.

- [ ] **Step 5: Add backend dependencies and quality commands**

Update `backend/pyproject.toml` to add:

- runtime config support if needed, using standard library env handling or `pydantic-settings`
- dev dependencies for `pytest`, `pytest-cov`, `ruff`, `mypy`
- script aliases or documented commands for `test`, `lint`, `format`, `typecheck`

Example target configuration:

```toml
[dependency-groups]
dev = [
  "mypy==1.18.2",
  "pytest==8.4.2",
  "pytest-cov==6.3.0",
  "ruff==0.13.1",
]
```

- [ ] **Step 6: Implement the app skeleton**

Write minimal code for:

- `app/settings.py` with a `Settings` class exposing `llm_enabled`
- `app/factory.py` with `create_app()`
- `app/routes.py` with health and extract routers
- `main.py` reduced to:

```python
from app.factory import create_app

app = create_app()
```

- [ ] **Step 7: Re-run the targeted backend tests**

Run: `cd backend && uv run pytest tests/unit/test_settings.py tests/integration/test_health.py -v`
Expected: PASS for both tests.

- [ ] **Step 8: Run backend quality commands**

Run:
- `cd backend && uv run ruff check .`
- `cd backend && uv run mypy .`
- `cd backend && uv run pytest -v`

Expected: all commands exit successfully.

- [ ] **Step 9: Commit**

```bash
git add backend/main.py backend/pyproject.toml backend/app backend/tests
git commit -m "refactor: add backend app factory and settings"
```

## Task 2: Extract Shared Domain Models And Response Contracts

**Files:**
- Create: `backend/domain/models.py`
- Create: `backend/domain/contracts.py`
- Modify: `backend/app/routes.py`
- Modify: `backend/services/orchestrator.py`
- Modify: `backend/services/rule_extractor.py`
- Modify: `backend/services/llm_extractor.py`
- Modify: `backend/services/normalizer.py`
- Create: `backend/tests/unit/test_normalizer.py`

- [ ] **Step 1: Write the failing normalization contract test**

```python
from services.normalizer import normalize_llm_payload


def test_normalizer_discards_edges_that_reference_missing_nodes():
    payload = {
        "nodes": [{"id": "张三", "label": "张三", "type": "person"}],
        "edges": [{"source": "张三", "target": "未知组织", "label": "就职于"}],
        "timeline": [],
    }
    result = normalize_llm_payload(payload)
    assert len(result.edges) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/test_normalizer.py::test_normalizer_discards_edges_that_reference_missing_nodes -v`
Expected: FAIL because the normalizer module and domain result types are not yet separated.

- [ ] **Step 3: Introduce domain models and contracts**

Create focused internal models for:

- extracted node
- extracted edge
- timeline event
- extraction result with `warnings`
- extractor contract interface or protocol

Suggested shape:

```python
@dataclass
class ExtractionResult:
    nodes: list[Node]
    edges: list[Edge]
    timeline: list[TimelineEvent]
    extraction_mode: str
    warnings: list[str]
```

- [ ] **Step 4: Move normalization into a dedicated service**

Implement `normalize_llm_payload()` in `backend/services/normalizer.py`, returning the shared extraction result model and rejecting invalid node types or dangling references.

- [ ] **Step 5: Re-run the targeted test**

Run: `cd backend && uv run pytest tests/unit/test_normalizer.py -v`
Expected: PASS.

- [ ] **Step 6: Run backend regression checks**

Run:
- `cd backend && uv run ruff check .`
- `cd backend && uv run mypy .`
- `cd backend && uv run pytest -v`

Expected: all pass with no contract mismatches.

- [ ] **Step 7: Commit**

```bash
git add backend/domain backend/services/normalizer.py backend/app/routes.py backend/tests/unit/test_normalizer.py
git commit -m "refactor: add extraction domain contracts"
```

## Task 3: Isolate Rule Extraction And LLM Extraction Behind An Orchestrator

**Files:**
- Create: `backend/services/orchestrator.py`
- Create: `backend/services/rule_extractor.py`
- Create: `backend/services/llm_extractor.py`
- Create: `backend/tests/unit/test_rule_extractor.py`
- Modify: `backend/app/settings.py`
- Modify: `backend/app/routes.py`

- [ ] **Step 1: Write the failing rule extractor test**

```python
from services.rule_extractor import RuleExtractor


def test_rule_extractor_finds_person_org_and_project_relationships():
    extractor = RuleExtractor()
    result = extractor.extract("张三在字节跳动做后端，上周参与电商项目。")
    assert {node.id for node in result.nodes} >= {"张三", "字节跳动", "电商项目"}
    assert any(edge.label == "就职于" for edge in result.edges)
    assert result.extraction_mode == "rules"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/test_rule_extractor.py -v`
Expected: FAIL because `RuleExtractor` does not yet exist.

- [ ] **Step 3: Write the failing fallback orchestration test**

Add to `backend/tests/integration/test_extract_api.py`:

```python
def test_extract_returns_warning_when_llm_fails_and_rules_succeed(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("services.llm_extractor.LLMExtractor.extract", _raise_llm_error)
    response = client.post("/extract", json={"text": "张三在字节跳动做后端。"})
    assert response.status_code == 200
    body = response.json()
    assert body["extraction_mode"] == "rules"
    assert body["warnings"]
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/test_rule_extractor.py tests/integration/test_extract_api.py -v`
Expected: FAIL because the orchestrator and warning surface are not implemented yet.

- [ ] **Step 5: Implement `RuleExtractor`**

Move the existing regex-based extraction logic into `backend/services/rule_extractor.py`, keeping current behavior as the compatibility baseline.

- [ ] **Step 6: Implement `LLMExtractor`**

Move provider selection and OpenAI-compatible request logic into `backend/services/llm_extractor.py`, isolating:

- provider config discovery
- request payload construction
- HTTP transport
- response parsing

- [ ] **Step 7: Implement `ExtractionOrchestrator`**

Create a service that:

- checks settings to decide whether LLM is enabled
- tries LLM first when configured
- falls back to rules when LLM is unavailable or invalid
- attaches warnings when fallback occurs

Minimal target API:

```python
class ExtractionOrchestrator:
    def extract(self, text: str) -> ExtractionResult:
        ...
```

- [ ] **Step 8: Re-run the targeted extractor tests**

Run: `cd backend && uv run pytest tests/unit/test_rule_extractor.py tests/integration/test_extract_api.py -v`
Expected: PASS, including warning assertions on fallback.

- [ ] **Step 9: Run full backend verification**

Run:
- `cd backend && uv run ruff check .`
- `cd backend && uv run mypy .`
- `cd backend && uv run pytest -v`

Expected: all pass.

- [ ] **Step 10: Commit**

```bash
git add backend/app backend/services backend/tests
git commit -m "refactor: isolate extractors behind orchestrator"
```

## Task 4: Add API Error Models, Request Validation, And Logging

**Files:**
- Create: `backend/app/errors.py`
- Modify: `backend/app/factory.py`
- Modify: `backend/app/routes.py`
- Modify: `backend/app/logging.py`
- Modify: `backend/tests/integration/test_extract_api.py`

- [ ] **Step 1: Write the failing invalid request test**

```python
def test_extract_rejects_blank_text(client):
    response = client.post("/extract", json={"text": ""})
    assert response.status_code == 422
```

- [ ] **Step 2: Run test to verify it fails if blank text is still accepted**

Run: `cd backend && uv run pytest tests/integration/test_extract_api.py::test_extract_rejects_blank_text -v`
Expected: FAIL if current request models still allow empty strings through.

- [ ] **Step 3: Write the failing internal error contract test**

```python
def test_extract_returns_structured_error_when_orchestrator_raises(client, monkeypatch):
    monkeypatch.setattr("app.routes.extract_text", _raise_internal_error)
    response = client.post("/extract", json={"text": "张三在字节跳动做后端。"})
    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "internal_error"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/integration/test_extract_api.py::test_extract_returns_structured_error_when_orchestrator_raises -v`
Expected: FAIL because structured exception handling is not implemented.

- [ ] **Step 5: Implement request validation**

Make the extract request model reject blank or whitespace-only text using Pydantic field validation.

- [ ] **Step 6: Implement API error handlers and logging hooks**

Add:

- structured error response payloads
- application-wide exception handlers
- request-safe logging for LLM fallback and unexpected failures

Example error payload:

```json
{
  "detail": {
    "code": "internal_error",
    "message": "An unexpected error occurred."
  }
}
```

- [ ] **Step 7: Re-run targeted API tests**

Run: `cd backend && uv run pytest tests/integration/test_extract_api.py -v`
Expected: PASS for invalid input, fallback, and structured error cases.

- [ ] **Step 8: Run backend verification**

Run:
- `cd backend && uv run ruff check .`
- `cd backend && uv run mypy .`
- `cd backend && uv run pytest -v`

Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add backend/app backend/tests/integration/test_extract_api.py
git commit -m "feat: add backend error handling and logging"
```

## Task 5: Introduce Frontend Build Tooling And Preserve Existing UI Behavior

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/eslint.config.js`
- Create: `frontend/.prettierrc.json`
- Create: `frontend/src/main.js`
- Create: `frontend/src/utils/examples.js`
- Create: `frontend/src/utils/to-elements.js`
- Create: `frontend/tests/to-elements.test.js`
- Modify: `frontend/index.html`

- [ ] **Step 1: Write the failing `toElements` unit test**

```javascript
import { describe, expect, it } from 'vitest';
import { toElements } from '../src/utils/to-elements';

describe('toElements', () => {
  it('maps nodes and edges into Cytoscape elements', () => {
    const result = toElements({
      nodes: [{ id: '张三', label: '张三', type: 'person', description: '人物' }],
      edges: [{ source: '张三', target: '字节跳动', label: '就职于' }],
    });
    expect(result).toHaveLength(2);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- --run frontend/tests/to-elements.test.js`
Expected: FAIL because the frontend toolchain and module do not exist yet.

- [ ] **Step 3: Create the frontend toolchain**

Add a lightweight Vite setup with scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "vitest"
  }
}
```

- [ ] **Step 4: Move example data and graph element transformation into modules**

Implement:

- `src/utils/examples.js`
- `src/utils/to-elements.js`
- `src/main.js` that boots the current page behavior

- [ ] **Step 5: Re-run the targeted frontend unit test**

Run: `cd frontend && npm test -- --run frontend/tests/to-elements.test.js`
Expected: PASS.

- [ ] **Step 6: Run frontend quality commands**

Run:
- `cd frontend && npm run lint`
- `cd frontend && npm run format:check`
- `cd frontend && npm test -- --run`
- `cd frontend && npm run build`

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/index.html frontend/package.json frontend/vite.config.js frontend/eslint.config.js frontend/.prettierrc.json frontend/src frontend/tests
git commit -m "build: add frontend toolchain and modules"
```

## Task 6: Modularize Frontend UI State And Add User-Visible Extraction Warnings

**Files:**
- Create: `frontend/src/api/extract.js`
- Create: `frontend/src/state/app-state.js`
- Create: `frontend/src/graph/render-graph.js`
- Create: `frontend/src/components/render-detail.js`
- Create: `frontend/src/components/render-status.js`
- Create: `frontend/src/components/render-timeline.js`
- Create: `frontend/src/components/render-json.js`
- Create: `frontend/src/components/bind-examples.js`
- Create: `frontend/tests/app-state.test.js`
- Create: `frontend/tests/ui-flow.test.js`
- Modify: `frontend/style.css`

- [ ] **Step 1: Write the failing state transition test**

```javascript
import { describe, expect, it } from 'vitest';
import { createInitialState, reduceAfterSuccess } from '../src/state/app-state';

describe('app state', () => {
  it('records warnings and extraction mode after success', () => {
    const next = reduceAfterSuccess(createInitialState(), {
      nodes: [],
      edges: [],
      timeline: [],
      extraction_mode: 'rules',
      warnings: ['LLM extraction failed; using rules.'],
    });
    expect(next.mode).toBe('rules');
    expect(next.warnings).toHaveLength(1);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- --run frontend/tests/app-state.test.js`
Expected: FAIL because state helpers do not exist yet.

- [ ] **Step 3: Write the failing UI flow test**

Use Testing Library with jsdom to assert:

- clicking generate updates loading text
- successful response renders timeline and JSON
- warning text appears when `warnings` is non-empty
- error response renders a readable failure message

- [ ] **Step 4: Run test to verify it fails**

Run: `cd frontend && npm test -- --run frontend/tests/ui-flow.test.js`
Expected: FAIL because the UI modules and state wiring are not yet implemented.

- [ ] **Step 5: Implement frontend state and API modules**

Add focused modules for:

- fetch wrapper and response handling
- state transitions
- graph rendering
- detail rendering
- timeline rendering
- status and warning rendering
- example selector wiring

- [ ] **Step 6: Expose extraction mode and warnings in the UI**

Update the page to show:

- loading status
- current extraction mode
- fallback warnings when present
- readable network or server error messages

- [ ] **Step 7: Re-run targeted frontend behavior tests**

Run: `cd frontend && npm test -- --run frontend/tests/app-state.test.js frontend/tests/ui-flow.test.js`
Expected: PASS.

- [ ] **Step 8: Run full frontend verification**

Run:
- `cd frontend && npm run lint`
- `cd frontend && npm run format:check`
- `cd frontend && npm test -- --run`
- `cd frontend && npm run build`

Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add frontend/src frontend/tests frontend/style.css
git commit -m "feat: add frontend state management and warning UI"
```

## Task 7: Add Open-Source Repo Hygiene, Unified Commands, And CI

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`
- Create: `.editorconfig`
- Create: `.env.example`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write the failing documentation checklist**

Create a manual acceptance checklist in the task branch covering:

- local backend setup instructions
- local frontend setup instructions
- quality commands
- fallback extraction explanation
- contributor workflow

Treat missing checklist items as failures to be resolved before commit.

- [ ] **Step 2: Write the failing CI command list**

Document the commands CI must run:

```text
cd backend && uv sync --dev && uv run ruff check . && uv run mypy . && uv run pytest -v
cd frontend && npm ci && npm run lint && npm run format:check && npm test -- --run && npm run build
```

Expected initial state: not yet automated in GitHub Actions.

- [ ] **Step 3: Implement repo metadata and docs**

Add:

- MIT license unless the maintainer specifies another license
- contributor guide with setup, quality gates, and PR expectations
- `.editorconfig`
- `.env.example`
- a rewritten README aligned with the first-phase architecture

- [ ] **Step 4: Implement CI workflow**

Create `.github/workflows/ci.yml` to:

- run on push and pull request
- install Python and Node
- run backend checks
- run frontend checks

- [ ] **Step 5: Re-run all local verification commands**

Run:
- `cd backend && uv sync --dev`
- `cd backend && uv run ruff check .`
- `cd backend && uv run mypy .`
- `cd backend && uv run pytest -v`
- `cd frontend && npm ci`
- `cd frontend && npm run lint`
- `cd frontend && npm run format:check`
- `cd frontend && npm test -- --run`
- `cd frontend && npm run build`

Expected: all pass locally before relying on CI.

- [ ] **Step 6: Commit**

```bash
git add README.md .gitignore .editorconfig .env.example LICENSE CONTRIBUTING.md .github/workflows/ci.yml
git commit -m "chore: add open-source docs and CI"
```

## Final Verification Checklist

- [ ] Run all backend checks from a clean shell
- [ ] Run all frontend checks from a clean shell
- [ ] Start backend locally and confirm `/` and `/docs` respond
- [ ] Start frontend locally and confirm graph generation still works
- [ ] Confirm warning UI appears when forcing LLM fallback
- [ ] Confirm README matches actual commands and file layout
- [ ] Review git diff for accidental scope creep

## Notes For The Implementer

- Preserve current product behavior unless the design explicitly changes it.
- Treat the existing regex extraction behavior as a compatibility baseline, not as something to improve during phase one.
- Prefer small commits after each task instead of a single large refactor commit.
- If toolchain choices need slight adjustment during implementation, preserve the design intent: lightweight, testable, contributor-friendly.
- Do not introduce new user-facing features in this phase.
