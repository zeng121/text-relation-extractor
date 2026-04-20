export function renderTimeline(timelineEl, timeline = []) {
  if (!timeline.length) {
    timelineEl.className = 'timeline muted';
    timelineEl.textContent = '暂无事件。';
    return;
  }

  timelineEl.className = 'timeline';
  timelineEl.innerHTML = timeline
    .map(
      (event) => `
        <div class="timeline-item">
          <div class="timeline-time">${event.time || '未标注时间'}</div>
          <div><strong>${event.label}</strong></div>
          <div class="timeline-detail">${event.detail || ''}</div>
        </div>
      `,
    )
    .join('');
}
