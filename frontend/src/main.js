import { DEFAULT_GRAPH_DATA, EXAMPLES } from './utils/examples.js';
import { extractGraphData } from './api/extract.js';
import { bindExampleSelector } from './components/bind-examples.js';
import { renderJson } from './components/render-json.js';
import { renderStatus } from './components/render-status.js';
import { renderTimeline } from './components/render-timeline.js';
import { createGraphRenderer } from './graph/render-graph.js';
import {
  applyAction,
  createInitialState,
  createSuccessAction,
} from './state/app-state.js';

function queryElements(doc) {
  return {
    exampleSelect: doc.getElementById('exampleSelect'),
    inputText: doc.getElementById('inputText'),
    generateBtn: doc.getElementById('generateBtn'),
    status: doc.getElementById('status'),
    graph: doc.getElementById('graph'),
    detailCard: doc.getElementById('detailCard'),
    timeline: doc.getElementById('timeline'),
    jsonOutput: doc.getElementById('jsonOutput'),
  };
}

function hasRequiredElements(elements) {
  return Boolean(
    elements.exampleSelect &&
    elements.inputText &&
    elements.generateBtn &&
    elements.status &&
    elements.graph &&
    elements.detailCard &&
    elements.timeline &&
    elements.jsonOutput,
  );
}

export function createApp({
  doc = document,
  fetchImpl = fetch,
  graphRenderer,
  apiBase,
} = {}) {
  let state = createInitialState();

  function bootstrap() {
    const elements = queryElements(doc);
    if (!hasRequiredElements(elements)) {
      return;
    }

    const renderGraph =
      graphRenderer ??
      createGraphRenderer({
        graphEl: elements.graph,
        detailEl: elements.detailCard,
      });

    bindExampleSelector({
      selectEl: elements.exampleSelect,
      inputEl: elements.inputText,
      examples: EXAMPLES,
    });

    renderStatus(elements.status, state, { doc });
    renderGraph(DEFAULT_GRAPH_DATA);
    renderTimeline(elements.timeline, DEFAULT_GRAPH_DATA.timeline || []);
    renderJson(elements.jsonOutput, DEFAULT_GRAPH_DATA);

    async function generateGraph() {
      const input = elements.inputText.value.trim();
      if (!input) {
        state = {
          ...createInitialState(),
          status: 'error',
          message: '先输入一点文本。',
        };
        renderStatus(elements.status, state, { doc });
        return;
      }

      state = applyAction(state, {
        type: 'EXTRACT_REQUESTED',
        inputText: input,
      });
      renderStatus(elements.status, state, { doc });

      try {
        const graphData = await extractGraphData({
          fetchImpl,
          apiBase,
          inputText: input,
        });
        state = applyAction(state, createSuccessAction(graphData));
        renderGraph(graphData);
        renderTimeline(elements.timeline, graphData.timeline || []);
        renderJson(elements.jsonOutput, graphData);
      } catch (error) {
        state = applyAction(state, { type: 'EXTRACT_FAILED', error });
      }

      renderStatus(elements.status, state, { doc });
    }

    elements.generateBtn.addEventListener('click', generateGraph);
  }

  return { bootstrap };
}

if (typeof document !== 'undefined' && document.getElementById('generateBtn')) {
  createApp().bootstrap();
}
