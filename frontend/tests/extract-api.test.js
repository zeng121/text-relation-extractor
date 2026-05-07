import { describe, expect, it } from 'vitest';

import { normalizeExtractionResponse } from '../src/api/extract.js';

describe('normalizeExtractionResponse', () => {
  it('normalizes the analysis contract fields', () => {
    const response = normalizeExtractionResponse({
      nodes: [{ id: '张三', label: '张三', type: 'person' }],
      edges: [
        {
          source: '张三',
          target: '后端',
          label: '负责',
          evidence_ids: ['ev-1'],
        },
      ],
      timeline: [{ id: 't1', label: '负责后端', evidence_ids: ['ev-1'] }],
      evidence: [
        { id: 'ev-1', text: '张三负责后端。', target_ids: ['张三', '后端'] },
      ],
      metadata: {
        extraction_mode: 'rules',
        provider: 'rules',
        duration_ms: 12,
        input_length: 7,
      },
      quality: {
        auto_created_nodes: 1,
        dropped_items: 2,
        fallback_used: false,
        warnings_count: 0,
      },
      extraction_mode: 'rules',
      warnings: ['  low confidence  '],
    });

    expect(response).toEqual({
      nodes: [{ id: '张三', label: '张三', type: 'person' }],
      edges: [
        {
          source: '张三',
          target: '后端',
          label: '负责',
          evidence_ids: ['ev-1'],
        },
      ],
      timeline: [{ id: 't1', label: '负责后端', evidence_ids: ['ev-1'] }],
      evidence: [
        { id: 'ev-1', text: '张三负责后端。', target_ids: ['张三', '后端'] },
      ],
      metadata: {
        extraction_mode: 'rules',
        provider: 'rules',
        duration_ms: 12,
        input_length: 7,
      },
      quality: {
        auto_created_nodes: 1,
        dropped_items: 2,
        fallback_used: false,
        warnings_count: 0,
      },
      extraction_mode: 'rules',
      warnings: ['low confidence'],
    });
  });

  it('fills safe defaults for missing analysis contract fields', () => {
    expect(normalizeExtractionResponse(null)).toEqual({
      nodes: [],
      edges: [],
      timeline: [],
      evidence: [],
      metadata: null,
      quality: {
        auto_created_nodes: 0,
        dropped_items: 0,
        fallback_used: false,
        warnings_count: 0,
      },
      extraction_mode: null,
      warnings: [],
    });
  });
});
