export function renderDetail(detailEl, node) {
  if (!node) {
    detailEl.className = 'card muted';
    detailEl.textContent = '点击图中的节点查看详情。';
    return;
  }

  detailEl.className = 'card';
  detailEl.innerHTML = `
    <strong>${node.id}</strong><br />
    类型：${node.type}<br />
    描述：${node.description || '暂无'}
  `;
}
