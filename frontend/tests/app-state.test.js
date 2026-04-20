import { describe, expect, it } from 'vitest';

import {
  applyAction,
  createInitialState,
  createSuccessAction,
} from '../src/state/app-state.js';

describe('app-state', () => {
  it('initializes in idle state', () => {
    expect(createInitialState()).toEqual({
      status: 'idle',
      message: '准备好了，点按钮试试。',
      graphData: null,
      extractionMode: null,
      warnings: [],
      error: null,
    });
  });

  it('transitions to loading when extraction starts', () => {
    const state = applyAction(createInitialState(), {
      type: 'EXTRACT_REQUESTED',
      inputText: 'hello',
    });

    expect(state.status).toBe('loading');
    expect(state.message).toBe('正在分析...');
    expect(state.error).toBeNull();
  });

  it('transitions to success and exposes extraction mode and warnings', () => {
    const action = createSuccessAction({
      nodes: [{ id: 'n1', label: 'n1', type: 'person' }],
      edges: [],
      timeline: [],
      extraction_mode: 'hybrid',
      warnings: ['时间线信息不完整'],
    });
    const state = applyAction(
      applyAction(createInitialState(), { type: 'EXTRACT_REQUESTED' }),
      action,
    );

    expect(state.status).toBe('success');
    expect(state.extractionMode).toBe('hybrid');
    expect(state.warnings).toEqual(['时间线信息不完整']);
    expect(state.message).toContain('生成完成');
  });

  it('transitions to error with a clear message', () => {
    const previous = applyAction(
      applyAction(createInitialState(), { type: 'EXTRACT_REQUESTED' }),
      createSuccessAction({
        nodes: [{ id: 'n1', label: 'n1', type: 'person' }],
        edges: [],
        timeline: [],
        extraction_mode: 'hybrid',
        warnings: ['时间线信息不完整'],
      }),
    );
    const state = applyAction(previous, {
      type: 'EXTRACT_FAILED',
      error: new Error('HTTP 500'),
    });

    expect(state.status).toBe('error');
    expect(state.error).toBe('HTTP 500');
    expect(state.message).toBe('出错了：HTTP 500');
    expect(state.extractionMode).toBeNull();
    expect(state.warnings).toEqual([]);
  });
});
