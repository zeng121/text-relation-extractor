const DEFAULT_API_BASE = 'http://127.0.0.1:8000';
const NETWORK_ERROR_MESSAGE = '网络请求失败，请稍后重试。';

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

function toErrorMessage(value) {
  return typeof value === 'string' && value.trim().length > 0
    ? value.trim()
    : null;
}

function getFallbackHttpErrorMessage(status) {
  if (status >= 500) {
    return '服务暂时不可用，请稍后重试。';
  }

  if (status >= 400) {
    return '请求失败，请检查输入后重试。';
  }

  return `HTTP ${status}`;
}

async function readResponseErrorMessage(response) {
  if (typeof response.json !== 'function') {
    return getFallbackHttpErrorMessage(response.status);
  }

  try {
    const payload = await response.json();
    return (
      toErrorMessage(payload?.detail?.message) ||
      toErrorMessage(payload?.detail) ||
      toErrorMessage(payload?.message) ||
      getFallbackHttpErrorMessage(response.status)
    );
  } catch {
    return getFallbackHttpErrorMessage(response.status);
  }
}

function normalizeRequestError(error) {
  if (!(error instanceof Error)) {
    return new Error(NETWORK_ERROR_MESSAGE);
  }

  const message = toErrorMessage(error.message);
  if (!message || message === 'Failed to fetch') {
    return new Error(NETWORK_ERROR_MESSAGE);
  }

  return error;
}

export async function extractGraphData({
  fetchImpl = fetch,
  apiBase = DEFAULT_API_BASE,
  inputText,
}) {
  try {
    const response = await fetchImpl(`${apiBase}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText }),
    });

    if (!response.ok) {
      throw new Error(await readResponseErrorMessage(response));
    }

    const payload = await response.json();
    return normalizeExtractionResponse(payload);
  } catch (error) {
    throw normalizeRequestError(error);
  }
}
