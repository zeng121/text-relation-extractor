# Remove Example Selector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the example dropdown from the frontend while keeping the current default Atlas text auto-filled in the textarea.

**Architecture:** Simplify the frontend boot flow so it no longer depends on an example selector element or example-binding helper. Keep the default text in a single constant and assign it during bootstrap before rendering the default graph state.

**Tech Stack:** Vite, Vitest, vanilla JS

---

### Task 1: Remove Selector UI And Keep Default Input Text

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/src/main.js`
- Modify: `frontend/src/utils/examples.js`
- Delete: `frontend/src/components/bind-examples.js`
- Modify: `frontend/tests/ui-flow.test.js`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run the targeted test file to verify failure**
- [ ] **Step 3: Implement the minimal UI and bootstrap changes**
- [ ] **Step 4: Re-run targeted and full frontend verification**
