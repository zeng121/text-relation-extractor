# Portfolio Analysis Workbench Upgrade Design

## Context

The current project is a local-first full-stack app that turns Chinese free-form text into a relationship graph, timeline, and structured JSON. It already has a FastAPI backend, a Vite frontend, tests, CI, README, license, and contribution guide. However, the user wants it to meet a stronger open-source portfolio standard: it should feel like a complete full-stack product, not a simple demo.

The target shape is a locally runnable portfolio project. It should demonstrate full-stack product engineering through a polished analysis workbench, clear architecture, reliable local setup, meaningful tests, and professional repository presentation.

## Key Decision: Do Not Introduce LangGraph In Phase One

Phase one will not introduce LangGraph or a similar AI workflow framework.

**Why:** the current core workflow is still a bounded request/response pipeline: accept text, extract structure, normalize results, enrich metadata, and render the analysis. LangGraph is more useful for long-running, stateful, multi-step agent workflows with durable execution or human-in-the-loop state editing. Adding it now would increase dependency and conceptual complexity without clearly improving the portfolio value.

**How to keep future optionality:** the backend will define a clear pipeline/provider boundary so a future LangGraph-backed implementation can replace the internals of the pipeline without changing the API contract or frontend data model.

## Goal

Upgrade the repository into a high-quality local-first full-stack portfolio project centered on a Chinese text relationship analysis workbench.

The upgraded project should let a user paste a complex text and inspect the extracted entities, relationships, timeline events, evidence, warnings, and JSON through multiple coordinated views.

## Non-Goals

Phase one does not include:

- LangGraph or another agent workflow framework
- authentication, accounts, databases, or saved project history
- cloud deployment or online demo hosting
- Docker as a required workflow
- PyPI or npm package publishing
- large community operations beyond basic open-source hygiene
- replacing the project theme with a generic AI platform

## Product Experience

The product should become a local analysis workbench rather than a single demo page.

### Main workflow

1. User opens the local frontend.
2. User reviews a strong built-in example or pastes their own Chinese text.
3. User clicks analyze.
4. The backend returns structured analysis.
5. The frontend displays the result through graph, summary, tables, timeline, evidence, and JSON views.
6. If LLM extraction fails and rules fallback is used, the UI shows this as a degraded-but-successful result.

### Workbench areas

- **Input panel**
  - large text input
  - high-quality built-in example text
  - analyze button
  - current mode/status feedback

- **Summary panel**
  - entity count
  - relationship count
  - timeline event count
  - evidence count
  - extraction mode
  - warnings or degraded status

- **Graph view**
  - Cytoscape graph
  - node type styling
  - node selection details
  - basic search/focus behavior so dense graphs remain usable

- **Structured views**
  - entity table: name, type, description, relationship count
  - relationship table: source, target, label, evidence link if available
  - timeline: time, event label, related entities, evidence link if available

- **Evidence and JSON panels**
  - evidence snippets tied to nodes, edges, or timeline events where possible
  - raw normalized JSON
  - copy JSON action

## Backend Design

The backend remains FastAPI and should evolve from a direct extractor service into an explicit analysis pipeline.

### Target structure

```text
backend/
  app/
    factory.py
    routes.py
    settings.py
    errors.py
    logging.py
  domain/
    models.py
    contracts.py
  services/
    pipeline.py
    providers/
      rule_provider.py
      llm_provider.py
    normalization.py
    evidence.py
    quality.py
```

This structure is conceptual; exact filenames can adapt to the existing repository during implementation.

### API layer

- Keep `POST /extract` as the main analysis endpoint.
- Add `GET /capabilities` to describe current backend capabilities, including LLM availability, supported node types, and version/status metadata.
- Keep API handlers thin: validate input, call the pipeline, convert domain results to response schemas.

### Pipeline layer

Introduce `ExtractionPipeline` as the single orchestration entry point.

Pipeline flow:

1. Accept validated input text and settings.
2. Choose extraction provider: LLM first when configured, otherwise rules-only.
3. Run provider extraction.
4. Normalize nodes, edges, timeline, and evidence.
5. Enrich the result with summary statistics and entity relationship counts.
6. Generate quality flags and warnings.
7. Return one unified analysis result.

If LLM extraction fails, the pipeline falls back to rules and returns a degraded success with warnings instead of treating the whole request as failed.

### Provider boundary

Both providers should implement the same interface:

- `RuleProvider`: deterministic local fallback; works without credentials.
- `LLMProvider`: owns provider selection, prompt, HTTP request, JSON extraction, and raw LLM response handling.

The frontend and API should not depend on which provider produced the result except through metadata.

### Domain model

The analysis result should extend the current graph-only response with explicit metadata and quality information.

Suggested top-level response fields:

- `nodes`
- `edges`
- `timeline`
- `evidence`
- `metadata`
- `quality`
- `warnings`

Suggested metadata:

- `extraction_mode`: `rules`, `llm`, or `fallback`
- `provider`: provider key or `rules`
- `duration_ms`
- `generated_at`
- `input_length`

Suggested quality information:

- number of auto-created nodes
- number of dropped invalid items
- whether fallback occurred
- low-confidence or incomplete extraction flags when available

## Frontend Design

The frontend can remain Vite plus modular JavaScript. A framework migration is not required for phase one because the project value comes from the full product experience and clean boundaries, not framework adoption.

### Target structure

```text
frontend/src/
  api/
    client.js
  state/
    reducer.js
    selectors.js
  views/
    input-panel.js
    summary-panel.js
    graph-view.js
    entities-table.js
    relations-table.js
    timeline-view.js
    evidence-panel.js
    json-panel.js
  graph/
    cytoscape-renderer.js
    graph-elements.js
  fixtures/
    examples.js
  utils/
    dom.js
    format.js
```

This structure is conceptual; exact filenames can adapt to the current code during implementation.

### State model

The UI should model these states explicitly:

- `idle`
- `loading`
- `success`
- `degraded`
- `error`

Fallback should map to `degraded`, not generic failure.

### View coordination

The workbench should support basic cross-view coordination:

- selecting a graph node updates the detail panel and can highlight the entity table row
- selecting an entity row can focus the graph node
- selecting an edge or timeline item can show related evidence
- JSON always reflects the normalized backend response

### Portfolio presentation

The default example should be rich enough to exercise all important views: people, organizations, projects, hardware/resources, documents/specs, deliverables, relationships, and timeline events.

The empty, loading, degraded, and error states should look intentional rather than incidental.

## Open-Source Repository Packaging

The repository should feel serious when opened on GitHub, while remaining honest about being a local-first portfolio project.

### README

Rewrite the README around:

- problem statement and project positioning
- screenshot of the upgraded workbench
- core capabilities
- 3-minute local setup
- backend/frontend development commands
- LLM key behavior and rules-only fallback
- API example
- quality checks
- current limitations
- roadmap

### Documentation

Add or update:

- `docs/architecture.md`: system architecture, data flow, pipeline boundaries
- `docs/api.md`: endpoints, request/response schema, metadata, warnings, errors
- `docs/development.md`: setup, test, lint, typecheck, build commands
- `docs/roadmap.md`: scoped roadmap for a portfolio-grade local app

### GitHub hygiene

Add basic templates:

- bug report issue template
- feature request issue template
- pull request template

Optional but acceptable:

- `CODE_OF_CONDUCT.md`
- `SECURITY.md` with local-first scope and secret-handling expectations

### Versioning and release feel

Add `CHANGELOG.md` and use SemVer language starting around `0.1.0`. Phase one does not require publishing packages or deployment artifacts.

## Testing And Quality Gates

Backend quality remains:

```bash
cd backend
uv run ruff check .
uv run mypy .
uv run pytest -v
```

Frontend quality remains:

```bash
cd frontend
npm run lint
npm run format:check
npm test -- --run
npm run build
```

Additional test focus:

- backend schema and normalization tests
- pipeline fallback/degraded-mode tests
- capability endpoint tests
- frontend API normalization tests
- frontend state reducer and selector tests
- graph element transformation tests
- jsdom UI flow tests for analyze success, degraded fallback, and error states

Coverage thresholds are not required in phase one; stable, meaningful tests are more important than an arbitrary number.

## Phased Delivery

### Phase 1: Define analysis contract and domain model

Goal: define the richer analysis result shape before rewriting UI or pipeline internals.

Deliverables:

- upgraded backend response/domain model
- `nodes`, `edges`, `timeline`, `evidence`, `metadata`, `quality`, `warnings`
- normalization tests
- frontend fixture updated to the new shape
- current `/extract` still returns displayable results

Acceptance criteria:

- backend tests cover schema and normalization behavior
- frontend tests can render or transform the new fixture shape
- existing core flow remains usable

### Phase 2: Productize backend pipeline

Goal: make backend behavior explicit, diagnosable, and extensible.

Deliverables:

- `ExtractionPipeline`
- provider interface with rule and LLM implementations
- evidence generation
- quality flags
- degraded fallback mode
- `GET /capabilities`
- unified API error shape

Acceptance criteria:

- rules mode works without credentials
- LLM failure returns degraded fallback with warnings
- response includes metadata, quality, and evidence where available
- backend quality gates pass

### Phase 3: Rebuild frontend workbench

Goal: make the product feel complete and portfolio-worthy.

Deliverables:

- workbench layout
- summary cards
- graph view
- entity and relation tables
- timeline view
- evidence panel
- JSON panel with copy action
- empty/loading/success/degraded/error states
- updated screenshot

Acceptance criteria:

- local UI demonstrates all core features with the default example
- degraded fallback is visible and understandable
- frontend tests cover state, API normalization, and key render flows
- frontend quality gates pass

### Phase 4: Open-source packaging

Goal: make the repository presentation match the product quality.

Deliverables:

- rewritten README
- architecture/API/development/roadmap docs
- issue templates
- PR template
- CHANGELOG
- CLAUDE.md update if commands or architecture change

Acceptance criteria:

- a new visitor can understand and run the project quickly
- docs match actual commands and behavior
- CI matches documented quality gates
- project limitations and roadmap are explicit

## Risks And Mitigations

### Risk: Scope expands into a platform rewrite

Mitigation: keep phase one local-first, stateless, and request/response. Defer saved history, authentication, deployments, and agent workflows.

### Risk: UI complexity grows without framework support

Mitigation: keep modules small and view-specific. If cross-view state becomes hard to manage after phase three, reassess whether a frontend framework is justified.

### Risk: LLM output remains inconsistent

Mitigation: keep normalization strict, show warnings, preserve rules fallback, and make quality flags visible.

### Risk: Open-source packaging becomes performative

Mitigation: only add documents and templates that match the actual project state. Be honest that this is a portfolio-grade local-first project, not an established large community project.

## Success Criteria

The upgrade succeeds when:

- the app feels like a real local analysis workbench
- the README and screenshot communicate value within seconds
- backend extraction behavior is explainable through pipeline, metadata, warnings, and quality flags
- frontend shows graph, tables, timeline, evidence, and JSON in coordinated views
- rules mode works without credentials
- LLM failure degrades gracefully
- documented backend and frontend quality gates pass
- the repository looks credible as a full-stack open-source portfolio project
