import cytoscape from 'cytoscape';

import { renderDetail } from '../components/render-detail.js';
import { toElements } from '../utils/to-elements.js';

export function createGraphRenderer({
  graphEl,
  detailEl,
  cytoscapeImpl = cytoscape,
  toElementsImpl = toElements,
}) {
  let cy;

  return function renderGraph(data) {
    const elements = toElementsImpl(data);
    if (cy) {
      cy.destroy();
      cy = undefined;
    }

    try {
      cy = cytoscapeImpl({
        container: graphEl,
        elements,
        style: [
          {
            selector: 'node',
            style: {
              'background-color': '#60a5fa',
              label: 'data(label)',
              color: '#e5e7eb',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': 12,
              'text-wrap': 'wrap',
              'text-max-width': 80,
              width: 58,
              height: 58,
              'border-width': 2,
              'border-color': '#dbeafe',
            },
          },
          {
            selector: 'edge',
            style: {
              width: 2,
              'line-color': '#94a3b8',
              'target-arrow-color': '#94a3b8',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              label: 'data(label)',
              color: '#cbd5e1',
              'font-size': 11,
              'text-background-color': '#0b1220',
              'text-background-opacity': 1,
              'text-background-padding': 2,
            },
          },
          {
            selector: 'node[type = "organization"]',
            style: { 'background-color': '#34d399' },
          },
          {
            selector: 'node[type = "project"]',
            style: { 'background-color': '#f59e0b' },
          },
          {
            selector: 'node[type = "role"]',
            style: { 'background-color': '#f472b6' },
          },
        ],
        layout: {
          name: 'cose',
          animate: true,
        },
      });

      cy.on('tap', 'node', (event) => {
        renderDetail(detailEl, event.target.data());
      });

      cy.on('tap', (event) => {
        if (event.target === cy) {
          renderDetail(detailEl, null);
        }
      });
      graphEl.textContent = '';
    } catch {
      graphEl.textContent = data.nodes?.length ? '图谱已生成。' : '暂无图谱。';
    }

    renderDetail(detailEl, null);
  };
}
