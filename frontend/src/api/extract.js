const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

function normalizeWarnings(input) {
  if (!Array.isArray(input)) {
    return [];
  }

  return input
    .map((warning) => String(warning).trim())
    .filter((warning) => warning.length > 0);
}

export function normalizeExtractionResponse(payload) {
  const safePayload = payload ?? {};

  return {
    nodes: Array.isArray(safePayload.nodes) ? safePayload.nodes : [],
    edges: Array.isArray(safePayload.edges) ? safePayload.edges : [],
    timeline: Array.isArray(safePayload.timeline) ? safePayload.timeline : [],
    extraction_mode:
      typeof safePayload.extraction_mode === 'string'
        ? safePayload.extraction_mode
        : null,
    warnings: normalizeWarnings(safePayload.warnings),
  };
}

export async function extractGraphData({
  fetchImpl = fetch,
  apiBase = DEFAULT_API_BASE,
  inputText,
}) {
  const response = await fetchImpl(`${apiBase}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: inputText }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const payload = await response.json();
  return normalizeExtractionResponse(payload);
}
