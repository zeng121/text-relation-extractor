import cytoscape from 'cytoscape';

import { DEFAULT_GRAPH_DATA, EXAMPLES } from './utils/examples.js';
import { toElements } from './utils/to-elements.js';

const API_BASE = 'http://127.0.0.1:8000';

let cy;

function renderDetail(node) {
  const card = document.getElementById('detailCard');
  if (!node) {
    card.className = 'card muted';
    card.textContent = '点击图中的节点查看详情。';
    return;
  }

  card.className = 'card';
  card.innerHTML = `
    <strong>${node.id}</strong><br />
    类型：${node.type}<br />
    描述：${node.description || '暂无'}
  `;
}

function renderTimeline(timeline = []) {
  const container = document.getElementById('timeline');
  if (!timeline.length) {
    container.className = 'timeline muted';
    container.textContent = '暂无事件。';
    return;
  }

  container.className = 'timeline';
  container.innerHTML = timeline
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

function bindGraphEvents() {
  cy.on('tap', 'node', (event) => {
    renderDetail(event.target.data());
  });

  cy.on('tap', (event) => {
    if (event.target === cy) {
      renderDetail(null);
    }
  });
}

function renderGraph(data) {
  const elements = toElements(data);

  if (cy) {
    cy.destroy();
  }

  cy = cytoscape({
    container: document.getElementById('graph'),
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

  bindGraphEvents();
  renderDetail(null);
  renderTimeline(data.timeline || []);
  document.getElementById('jsonOutput').textContent = JSON.stringify(
    data,
    null,
    2,
  );
}

async function generateGraph() {
  const input = document.getElementById('inputText').value.trim();
  const status = document.getElementById('status');

  if (!input) {
    status.textContent = '先输入一点文本。';
    return;
  }

  status.textContent = '正在分析...';

  try {
    const response = await fetch(`${API_BASE}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: input }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    renderGraph(data);
    status.textContent = `生成完成：${data.nodes.length} 个节点，${data.edges.length} 条关系。`;
  } catch (error) {
    status.textContent = `出错了：${error.message}`;
  }
}

function bindExampleSelector() {
  const select = document.getElementById('exampleSelect');
  select.addEventListener('change', (event) => {
    document.getElementById('inputText').value =
      EXAMPLES[event.target.value] || EXAMPLES.default;
  });
}

document.getElementById('inputText').value = EXAMPLES.default;
document.getElementById('generateBtn').addEventListener('click', generateGraph);
bindExampleSelector();
renderGraph(DEFAULT_GRAPH_DATA);
