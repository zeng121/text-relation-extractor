export function renderTimeline(timelineEl, timeline = []) {
  if (!timeline.length) {
    timelineEl.className = 'timeline muted';
    timelineEl.textContent = '暂无事件。';
    return;
  }

  timelineEl.className = 'timeline';
  timelineEl.replaceChildren();

  timeline.forEach((event) => {
    const itemEl = document.createElement('div');
    itemEl.className = 'timeline-item';

    const timeEl = document.createElement('div');
    timeEl.className = 'timeline-time';
    timeEl.textContent = event.time || '未标注时间';
    itemEl.append(timeEl);

    const labelRowEl = document.createElement('div');
    const labelEl = document.createElement('strong');
    labelEl.textContent = event.label;
    labelRowEl.append(labelEl);
    itemEl.append(labelRowEl);

    const detailEl = document.createElement('div');
    detailEl.className = 'timeline-detail';
    detailEl.textContent = event.detail || '';
    itemEl.append(detailEl);

    timelineEl.append(itemEl);
  });
}
