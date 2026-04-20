# Text Graph MVP Production-Grade Engineering Upgrade Design

## Context

This repository is currently a toy full-stack MVP:

- The backend is a small FastAPI service with a single `/extract` API.
- Extraction logic is concentrated in one module with direct environment access, LLM fallback behavior, and minimal error visibility.
- The frontend is a static page with a single JavaScript file that renders graph, detail, timeline, and JSON output.
- The project has no automated tests, CI, license, contribution guide, or open-source repo hygiene.

The approved scope for phase one is:

- Prioritize local development quality over deployment infrastructure.
- Upgrade both backend and frontend.
- Allow moderate toolchain improvements without switching to a heavyweight frontend framework.

## Goal

Turn the repository into an engineering-grade open-source project that remains lightweight, keeps the current product scope, and is maintainable, testable, and reviewable by outside contributors.

## Non-Goals

Phase one explicitly does not include:

- Rebuilding the frontend in React, Vue, or another heavy framework
- Adding databases, authentication, background jobs, or user accounts
- Expanding product scope with uploads, exports, clustering views, or new graph features
- Building production deployment infrastructure such as containers, reverse proxies, or CI/CD release pipelines
- Adding complex observability stacks beyond useful local logging and diagnosable errors

## Approach Options

### Option 1: Minimal Hardening

Keep the current structure mostly intact and add tests, docs, and CI around it.

Pros:

- Smallest code delta
- Lowest migration risk

Cons:

- Preserves weak module boundaries
- Frontend remains harder to test and extend
- Backend continues to couple transport, orchestration, and extraction details

### Option 2: Moderate Engineering Upgrade

Keep FastAPI and a lightweight browser app, but introduce explicit module boundaries, a small frontend build/test toolchain, unified quality gates, and open-source repo standards.

Pros:

- Best balance of quality, maintainability, and implementation scope
- Keeps the repository approachable
- Produces a credible open-source baseline without rewriting the product

Cons:

- Requires one-time restructuring on both backend and frontend
- Slightly raises contributor setup complexity compared with pure static files

### Option 3: Full Frontend Rebuild

Retain backend goals but replace the frontend with a modern framework and a more complete application stack.

Pros:

- Highest long-term frontend ceiling

Cons:

- Turns phase one into a rewrite
- Increases scope, migration cost, and maintenance overhead

## Recommended Design

Choose Option 2.

This phase should focus on making the existing product reliable and maintainable rather than changing what the product is. The repository should feel small but serious: clear module boundaries, deterministic local setup, stable tests, explicit failure modes, and standard open-source project metadata.

## Architecture

### Backend

The backend should move from a script-like layout to a layered structure:

- `backend/app/` for application factory, API routes, settings, logging, and error handling
- `backend/domain/` for graph extraction domain models and protocol boundaries
- `backend/services/` for extraction orchestration, rule extraction, LLM extraction, and response normalization
- `backend/tests/` for automated verification

Design principles:

- `main.py` should only assemble and expose the FastAPI app.
- Environment variables should be read through a single settings object.
- Rule extraction and LLM extraction should be separate implementations behind a common interface.
- One orchestration service should decide how extraction runs, how fallback works, and which warnings or metadata are returned.
- API transport models should be separate from internal service models when responsibilities differ.

### Frontend

The frontend should remain lightweight but become modular:

- `frontend/src/main.js` as the entry point
- `frontend/src/api/` for HTTP calls
- `frontend/src/state/` for result and UI state transitions
- `frontend/src/graph/` for Cytoscape integration
- `frontend/src/components/` for timeline, detail panel, status, and example input UI
- `frontend/src/utils/` for pure helpers
- `frontend/tests/` for module and UI behavior tests

The frontend should use a lightweight build/test toolchain to support:

- ES module organization
- dev server workflow
- frontend tests
- linting and formatting

The UI scope stays the same:

- text input
- example text switching
- graph rendering
- node detail panel
- timeline rendering
- structured JSON output

## Data Flow

The extraction flow should become explicit:

1. Frontend submits text to the backend extract API.
2. Backend validates the request.
3. Extraction orchestrator decides which extractor to try first.
4. If LLM extraction is configured, the LLM extractor runs and returns normalized structured output.
5. If LLM extraction is unavailable or invalid, the orchestrator falls back to rule extraction.
6. Backend returns nodes, edges, timeline, extraction mode, and warnings.
7. Frontend updates graph, timeline, detail state, JSON output, and user-visible status messaging.

This keeps fallback behavior while making it visible and diagnosable.

## Error Handling

Current behavior is too opaque because LLM failures silently degrade to rules. The upgraded design should keep resilience without hiding operational state.

Backend requirements:

- Distinguish invalid request errors, upstream LLM request failures, malformed LLM response failures, and unexpected internal failures.
- Return user-safe error payloads for real API failures.
- Include `extraction_mode` in successful responses and add `warnings` when fallback happens.
- Log fallback reasons and internal exceptions with enough detail for debugging.

Frontend requirements:

- Show clear loading, empty, success, warning, and error states.
- Display which extraction mode produced the current result.
- Show fallback or degraded-mode warnings without breaking the workflow.
- Replace generic HTTP error text with understandable messages tied to likely user actions.

## Configuration

Configuration should be centralized and documented.

Requirements:

- A backend settings module should own all environment access.
- Provide `.env.example` with documented keys and defaults where appropriate.
- Missing LLM credentials should not be treated as an application error; they should simply disable LLM-first extraction.
- Development commands should be standardized and documented for both backend and frontend.

## Testing Strategy

Phase one should establish a credible automated test baseline.

Backend:

- Unit tests for rule extraction behavior
- Unit tests for LLM output normalization and validation
- Integration tests for the extract API and fallback behavior

Frontend:

- Tests for pure transformation and state logic
- Tests for key UI behavior such as status updates, timeline rendering, and error rendering

Repository quality:

- Lint
- Format check
- Type-oriented checks where the chosen tools support them
- Test commands for backend and frontend

End-to-end browser automation is intentionally deferred. The first quality bar should be fast, reliable unit and integration coverage.

## Open-Source Repository Standards

To reach credible GitHub open-source quality, the repository should add:

- `LICENSE`
- `CONTRIBUTING.md`
- improved `README.md`
- `.editorconfig`
- CI workflow under `.github/workflows/`
- development setup instructions
- project quality command reference

The README should explain:

- what the project does
- current capabilities and limitations
- how to run backend and frontend locally
- how fallback extraction works
- how to run checks and tests
- how contributors should get started

## Proposed Directory Shape

```text
text-graph-mvp/
├── .github/
│   └── workflows/
├── backend/
│   ├── app/
│   ├── domain/
│   ├── services/
│   ├── tests/
│   ├── main.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── tests/
│   ├── package.json
│   └── ...
├── docs/
│   └── superpowers/
│       └── specs/
├── .editorconfig
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Milestones

### Milestone 1: Backend Restructure

- Introduce app factory and centralized settings
- Split extraction orchestration from concrete extractors
- Preserve API behavior while improving error visibility
- Add backend tests

### Milestone 2: Frontend Modularization

- Introduce a lightweight build/test workflow
- Split UI logic by responsibility
- Add visible extraction mode and warning states
- Add frontend tests for key behaviors

### Milestone 3: Repo Quality Baseline

- Add quality commands and CI
- Update README and contributor documentation
- Add license and project metadata

## Success Criteria

Phase one is successful when:

- a new contributor can follow documented local setup and run the project
- backend and frontend have automated tests that cover core behaviors
- the repository has repeatable quality commands and CI to enforce them
- extraction fallback behavior is visible to both users and developers
- code structure is modular enough that future features can be added without editing monolithic files
- the repository is publishable as a serious open-source project without obvious hygiene gaps

## Risks And Mitigations

### Risk: Over-scoping Phase One

Mitigation:

- Preserve current product scope
- Defer infrastructure and product expansion work
- Optimize for maintainability, not feature count

### Risk: Tooling Complexity Outgrows Project Size

Mitigation:

- Prefer lightweight tools
- Introduce only tooling that directly improves testing, modularity, or contributor workflow

### Risk: Frontend Refactor Breaks Existing Behavior

Mitigation:

- Preserve UI surface area
- Add focused tests around current visible behaviors before or during modularization

### Risk: LLM Integration Remains Brittle

Mitigation:

- Isolate LLM client logic
- Treat fallback as a first-class, documented path
- Validate all normalized output before returning success
