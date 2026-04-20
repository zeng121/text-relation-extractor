function ensureModeElement(doc, statusEl) {
  const existing = doc.getElementById('modeBadge');
  if (existing) {
    return existing;
  }

  const modeEl = doc.createElement('div');
  modeEl.id = 'modeBadge';
  modeEl.className = 'mode-badge muted';
  modeEl.textContent = '抽取模式：-';
  statusEl.insertAdjacentElement('afterend', modeEl);
  return modeEl;
}

function ensureWarningElement(doc, modeEl) {
  const existing = doc.getElementById('warningList');
  if (existing) {
    return existing;
  }

  const warningEl = doc.createElement('div');
  warningEl.id = 'warningList';
  warningEl.className = 'warning-list muted';
  warningEl.textContent = '告警：无';
  modeEl.insertAdjacentElement('afterend', warningEl);
  return warningEl;
}

function renderWarnings(warningEl, warnings, doc) {
  warningEl.replaceChildren();

  const titleEl = doc.createElement('strong');
  titleEl.textContent = '告警：';
  warningEl.append(titleEl);

  const listEl = doc.createElement('ul');
  warnings.forEach((warning) => {
    const itemEl = doc.createElement('li');
    itemEl.textContent = warning;
    listEl.append(itemEl);
  });
  warningEl.append(listEl);
}

export function renderStatus(statusEl, state, { doc = document } = {}) {
  const modeEl = ensureModeElement(doc, statusEl);
  const warningEl = ensureWarningElement(doc, modeEl);

  statusEl.className = `status status-${state.status}`;
  statusEl.textContent = state.message;

  modeEl.className = state.extractionMode ? 'mode-badge' : 'mode-badge muted';
  modeEl.textContent = `抽取模式：${state.extractionMode || '-'}`;

  if (!state.warnings.length) {
    warningEl.className = 'warning-list muted';
    warningEl.textContent = '告警：无';
    return;
  }

  warningEl.className = 'warning-list';
  renderWarnings(warningEl, state.warnings, doc);
}
