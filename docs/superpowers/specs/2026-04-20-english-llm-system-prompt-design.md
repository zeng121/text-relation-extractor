# English LLM System Prompt Design

## Goal

Replace the backend LLM system prompt text with an English version while preserving the current extraction contract and behavior constraints.

## Scope

- Modify only the backend system prompt string.
- Keep the JSON schema, node type list, and "JSON only" requirement unchanged.
- Add a focused test that protects the prompt contract.

## Approach

The change should remain text-only. The prompt will continue instructing the model to extract a graph from Chinese user input, but the instruction text itself will be written in English. This avoids accidental behavior drift from changing prompt structure, payload shape, or downstream normalization logic.
