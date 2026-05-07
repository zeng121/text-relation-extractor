export function toElements(data) {
  const nodeElements = data.nodes.map((node) => ({
    data: {
      id: node.id,
      label: `${node.label}\n(${node.type})`,
      type: node.type,
      description: node.description || '',
    },
  }));

  const edgeElements = data.edges.map((edge, index) => ({
    data: {
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      evidenceIds: Array.isArray(edge.evidence_ids) ? edge.evidence_ids : [],
    },
  }));

  return [...nodeElements, ...edgeElements];
}
