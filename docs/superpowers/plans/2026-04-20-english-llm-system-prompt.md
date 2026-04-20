# English LLM System Prompt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the backend LLM system prompt text with English while preserving the existing extraction contract.

**Architecture:** Keep the prompt in `backend/services/llm_extractor.py` as a single constant. Add a focused unit test that verifies the prompt stays English-oriented while still enforcing JSON-only output and the supported node-type list.

**Tech Stack:** Python, pytest

---

### Task 1: Translate The Prompt Without Changing Its Contract

**Files:**
- Modify: `backend/services/llm_extractor.py`
- Create: `backend/tests/unit/test_llm_extractor.py`

- [ ] **Step 1: Write the failing test**

Add a test that asserts the prompt contains the JSON-only instruction and the supported type list in English.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/test_llm_extractor.py -v`
Expected: FAIL because the current prompt text is still Chinese.

- [ ] **Step 3: Write minimal implementation**

Translate the existing system prompt into English without changing the contract structure.

- [ ] **Step 4: Run targeted and full verification**

Run:
- `cd backend && uv run pytest tests/unit/test_llm_extractor.py -v`
- `cd backend && uv run pytest -v`

Expected: PASS.
