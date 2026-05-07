function removeDuplicateNodeLabels(data) {
  if (!data || typeof data !== 'object' || !Array.isArray(data.nodes)) {
    return data;
  }

  return {
    ...data,
    nodes: data.nodes.map((node) => {
      if (!node || typeof node !== 'object' || node.id !== node.label) {
        return node;
      }

      const nodeWithoutDuplicateLabel = { ...node };
      delete nodeWithoutDuplicateLabel.label;
      return nodeWithoutDuplicateLabel;
    }),
  };
}

export function renderJson(jsonEl, data) {
  jsonEl.textContent = JSON.stringify(removeDuplicateNodeLabels(data), null, 2);
}
