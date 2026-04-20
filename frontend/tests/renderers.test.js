/** @vitest-environment jsdom */

import { describe, expect, it } from 'vitest';

import { renderDetail } from '../src/components/render-detail.js';
import { renderTimeline } from '../src/components/render-timeline.js';

describe('renderers', () => {
  it('renders detail content as text instead of HTML', () => {
    const detailEl = document.createElement('div');

    renderDetail(detailEl, {
      id: '<img src=x onerror=alert(1)>',
      type: 'person',
      description: '<script>alert(1)</script>',
    });

    expect(detailEl.textContent).toContain('<img src=x onerror=alert(1)>');
    expect(detailEl.textContent).toContain('<script>alert(1)</script>');
    expect(detailEl.querySelector('img')).toBeNull();
    expect(detailEl.querySelector('script')).toBeNull();
  });

  it('renders timeline content as text instead of HTML', () => {
    const timelineEl = document.createElement('div');

    renderTimeline(timelineEl, [
      {
        time: '<img src=x onerror=alert(1)>',
        label: '<strong>unsafe</strong>',
        detail: '<script>alert(1)</script>',
      },
    ]);

    expect(timelineEl.textContent).toContain('<img src=x onerror=alert(1)>');
    expect(timelineEl.textContent).toContain('<strong>unsafe</strong>');
    expect(timelineEl.textContent).toContain('<script>alert(1)</script>');
    expect(timelineEl.querySelector('img')).toBeNull();
    expect(timelineEl.querySelector('script')).toBeNull();
  });
});
