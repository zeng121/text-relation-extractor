# Dangling Edge Repair And Prompt Tightening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve LLM-extracted relationships when edge endpoints are missing from `nodes`, and strengthen the prompt to reduce future dangling edges.

**Architecture:** Update the backend normalizer to auto-create missing endpoint nodes with lightweight type inference instead of discarding those edges. Tighten the English system prompt so the model explicitly verifies that every edge endpoint also appears in `nodes`, especially for reports, specs, hardware, resources, and deliverables.

**Tech Stack:** Python, pytest

---

### Task 1: Repair Missing Nodes During Normalization

**Files:**
- Modify: `backend/services/normalizer.py`
- Modify: `backend/tests/unit/test_normalizer.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run the targeted tests to verify they fail**
- [ ] **Step 3: Implement minimal missing-node inference and warning behavior**
- [ ] **Step 4: Re-run the targeted tests to verify they pass**

### Task 2: Tighten The English Prompt Contract

**Files:**
- Modify: `backend/services/llm_extractor.py`
- Modify: `backend/tests/unit/test_llm_extractor.py`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run the targeted test to verify it fails**
- [ ] **Step 3: Update the prompt without changing schema**
- [ ] **Step 4: Run backend verification**
