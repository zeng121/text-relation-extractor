/** @vitest-environment jsdom */

import { describe, expect, it } from 'vitest';

import { renderDetail } from '../src/components/render-detail.js';
import { renderTimeline } from '../src/components/render-timeline.js';
import { createGraphRenderer } from '../src/graph/render-graph.js';

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

  it('keeps graph canvas mounted after Cytoscape initializes', () => {
    const graphEl = document.createElement('div');
    const detailEl = document.createElement('div');

    const renderGraph = createGraphRenderer({
      graphEl,
      detailEl,
      cytoscapeImpl: ({ container }) => {
        const canvas = document.createElement('canvas');
        container.append(canvas);
        return {
          destroy() {},
          on() {},
        };
      },
    });

    renderGraph({
      nodes: [{ id: '张三', label: '张三', type: 'person' }],
      edges: [],
    });

    expect(graphEl.querySelector('canvas')).not.toBeNull();
  });
});
