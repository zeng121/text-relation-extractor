const INITIAL_MESSAGE = '准备好了，点按钮试试。';

export function createInitialState() {
  return {
    status: 'idle',
    message: INITIAL_MESSAGE,
    graphData: null,
    extractionMode: null,
    warnings: [],
    error: null,
  };
}

export function createSuccessAction(graphData) {
  return {
    type: 'EXTRACT_SUCCEEDED',
    graphData,
  };
}

function buildSuccessMessage(graphData) {
  const nodeCount = graphData?.nodes?.length ?? 0;
  const edgeCount = graphData?.edges?.length ?? 0;
  return `生成完成：${nodeCount} 个节点，${edgeCount} 条关系。`;
}

export function applyAction(state, action) {
  switch (action.type) {
    case 'EXTRACT_REQUESTED':
      return {
        ...state,
        status: 'loading',
        message: '正在分析...',
        extractionMode: null,
        warnings: [],
        error: null,
      };
    case 'EXTRACT_SUCCEEDED':
      return {
        ...state,
        status: 'success',
        message: buildSuccessMessage(action.graphData),
        graphData: action.graphData,
        extractionMode: action.graphData?.extraction_mode ?? null,
        warnings: action.graphData?.warnings ?? [],
        error: null,
      };
    case 'EXTRACT_FAILED':
      return {
        ...state,
        status: 'error',
        message: `出错了：${action.error.message}`,
        extractionMode: null,
        warnings: [],
        error: action.error.message,
      };
    default:
      return state;
  }
}
