/** @vitest-environment jsdom */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { EXAMPLES } from '../src/utils/examples.js';
import { createApp } from '../src/main.js';

async function flushMicrotasks(times = 6) {
  for (let index = 0; index < times; index += 1) {
    await Promise.resolve();
  }
}

function createDom() {
  document.body.innerHTML = `
    <div class="app">
      <aside class="panel input-panel">
        <select id="exampleSelect">
          <option value="default">团队协作</option>
          <option value="startup">创业项目</option>
          <option value="campus">校园活动</option>
        </select>
        <textarea id="inputText"></textarea>
        <button id="generateBtn">生成图谱</button>
        <p id="status"></p>
      </aside>
      <main class="panel graph-panel"><div id="graph"></div></main>
      <aside class="panel result-panel">
        <div id="modeBadge"></div>
        <div id="warningList"></div>
        <div id="detailCard"></div>
        <div id="timeline"></div>
        <pre id="jsonOutput"></pre>
      </aside>
    </div>
  `;
}

function createDeferred() {
  let resolve;
  let reject;
  const promise = new Promise((nextResolve, nextReject) => {
    resolve = nextResolve;
    reject = nextReject;
  });
  return { promise, resolve, reject };
}

describe('ui flow', () => {
  beforeEach(() => {
    createDom();
  });

  it('shows loading state and updates status/mode/warnings when extraction succeeds', async () => {
    const deferred = createDeferred();
    const fetchImpl = vi.fn(async () => {
      await deferred.promise;
      return {
        ok: true,
        json: async () => ({
          nodes: [{ id: '张三', label: '张三', type: 'person' }],
          edges: [],
          timeline: [{ label: '加入项目', time: '上周' }],
          extraction_mode: 'hybrid',
          warnings: ['部分关系来自推断'],
        }),
      };
    });
    const graphRenderer = vi.fn();

    const app = createApp({ fetchImpl, graphRenderer });
    app.bootstrap();

    document.getElementById('inputText').value = '张三加入项目';
    document.getElementById('generateBtn').click();

    expect(document.getElementById('status').textContent).toBe('正在分析...');

    deferred.resolve();
    await flushMicrotasks();

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(graphRenderer).toHaveBeenCalledTimes(2);
    expect(document.getElementById('status').textContent).toContain('生成完成');
    expect(document.getElementById('modeBadge').textContent).toContain(
      'hybrid',
    );
    expect(document.getElementById('warningList').textContent).toContain(
      '部分关系来自推断',
    );
    expect(document.getElementById('timeline').textContent).toContain(
      '加入项目',
    );
    expect(document.getElementById('jsonOutput').textContent).toContain(
      '"extraction_mode": "hybrid"',
    );
  });

  it('renders a readable server error message when extraction fails', async () => {
    const fetchImpl = vi.fn(async () => ({
      ok: false,
      status: 503,
      json: async () => ({
        detail: {
          code: 'internal_error',
          message: 'An unexpected error occurred.',
        },
      }),
    }));
    const graphRenderer = vi.fn();

    const app = createApp({ fetchImpl, graphRenderer });
    app.bootstrap();

    document.getElementById('inputText').value = '张三加入项目';
    document.getElementById('generateBtn').click();
    await flushMicrotasks();

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(document.getElementById('status').textContent).toBe(
      '出错了：An unexpected error occurred.',
    );
    expect(document.getElementById('modeBadge').textContent).toContain('-');
    expect(document.getElementById('warningList').textContent).toContain(
      '告警：无',
    );
  });

  it('renders a readable network error message when fetch rejects', async () => {
    const fetchImpl = vi.fn(async () => {
      throw new Error('网络请求失败，请稍后重试。');
    });
    const graphRenderer = vi.fn();

    const app = createApp({ fetchImpl, graphRenderer });
    app.bootstrap();

    document.getElementById('inputText').value = '张三加入项目';
    document.getElementById('generateBtn').click();
    await flushMicrotasks();

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(document.getElementById('status').textContent).toBe(
      '出错了：网络请求失败，请稍后重试。',
    );
    expect(document.getElementById('modeBadge').textContent).toContain('-');
    expect(document.getElementById('warningList').textContent).toContain(
      '告警：无',
    );
  });

  it('updates status/mode/warnings when extraction succeeds', async () => {
    const fetchImpl = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        nodes: [{ id: '张三', label: '张三', type: 'person' }],
        edges: [],
        timeline: [{ label: '加入项目', time: '上周' }],
        extraction_mode: 'hybrid',
        warnings: ['部分关系来自推断'],
      }),
    }));
    const graphRenderer = vi.fn();

    const app = createApp({ fetchImpl, graphRenderer });
    app.bootstrap();

    document.getElementById('inputText').value = '张三加入项目';
    document.getElementById('generateBtn').click();
    await flushMicrotasks();

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(graphRenderer).toHaveBeenCalledTimes(2);
    expect(document.getElementById('status').textContent).toContain('生成完成');
    expect(document.getElementById('modeBadge').textContent).toContain(
      'hybrid',
    );
    expect(document.getElementById('warningList').textContent).toContain(
      '部分关系来自推断',
    );
  });

  it('clears extraction metadata when submitting an empty input after success', async () => {
    const fetchImpl = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        nodes: [{ id: '张三', label: '张三', type: 'person' }],
        edges: [],
        timeline: [],
        extraction_mode: 'hybrid',
        warnings: ['部分关系来自推断'],
      }),
    }));

    const app = createApp({ fetchImpl, graphRenderer: vi.fn() });
    app.bootstrap();

    document.getElementById('inputText').value = '张三加入项目';
    document.getElementById('generateBtn').click();
    await flushMicrotasks();

    document.getElementById('inputText').value = '   ';
    document.getElementById('generateBtn').click();
    await flushMicrotasks();

    expect(document.getElementById('status').textContent).toBe(
      '先输入一点文本。',
    );
    expect(document.getElementById('modeBadge').textContent).toContain('-');
    expect(document.getElementById('warningList').textContent).toContain(
      '告警：无',
    );
  });

  it('renders warnings as text instead of HTML', async () => {
    const fetchImpl = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        nodes: [{ id: '张三', label: '张三', type: 'person' }],
        edges: [],
        timeline: [],
        extraction_mode: 'hybrid',
        warnings: ['<img src=x onerror=alert(1)> unsafe'],
      }),
    }));

    const app = createApp({ fetchImpl, graphRenderer: vi.fn() });
    app.bootstrap();

    document.getElementById('inputText').value = '张三加入项目';
    document.getElementById('generateBtn').click();
    await flushMicrotasks();

    const warningList = document.getElementById('warningList');
    expect(warningList.textContent).toContain(
      '<img src=x onerror=alert(1)> unsafe',
    );
    expect(warningList.querySelector('img')).toBeNull();
  });

  it('binds example selector changes into input text', () => {
    const app = createApp({ fetchImpl: vi.fn(), graphRenderer: vi.fn() });
    app.bootstrap();

    const select = document.getElementById('exampleSelect');
    select.value = 'startup';
    select.dispatchEvent(new Event('change'));

    expect(document.getElementById('inputText').value).toBe(EXAMPLES.startup);
  });
});
