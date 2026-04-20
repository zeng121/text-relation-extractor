import { describe, expect, it } from 'vitest';

import { toElements } from '../src/utils/to-elements.js';

describe('toElements', () => {
  it('maps nodes and edges to Cytoscape elements', () => {
    const data = {
      nodes: [
        {
          id: '张三',
          label: '张三',
          type: 'person',
          description: '后端工程师',
        },
        { id: '字节跳动', label: '字节跳动', type: 'organization' },
      ],
      edges: [{ source: '张三', target: '字节跳动', label: '就职于' }],
    };

    expect(toElements(data)).toEqual([
      {
        data: {
          id: '张三',
          label: '张三\n(person)',
          type: 'person',
          description: '后端工程师',
        },
      },
      {
        data: {
          id: '字节跳动',
          label: '字节跳动\n(organization)',
          type: 'organization',
          description: '',
        },
      },
      {
        data: {
          id: 'edge-0',
          source: '张三',
          target: '字节跳动',
          label: '就职于',
        },
      },
    ]);
  });
});
