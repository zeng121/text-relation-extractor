export function renderJson(jsonEl, data) {
  jsonEl.textContent = JSON.stringify(data, null, 2);
}
